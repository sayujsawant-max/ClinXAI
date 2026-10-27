"""Generate explanation evidence: SHAP global/local plots, LIME plots, LIME-vs-SHAP comparison over
the whole held-out test set, and programmatically selected case studies.

Usage:  python evaluate.py        (requires python train_model.py first)
"""
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import (
    CASE_STUDIES_DIR,
    CLASS_NAMES,
    DECISION_THRESHOLD,
    FIGURES_DIR,
    METRICS_DIR,
    TOP_K,
    ensure_dirs,
)
from src.comparison import compare_explanations, lime_stability, select_case_studies
from src.explain_lime import explain_patient_lime
from src.explain_shap import additivity_error, build_tree_explainer, compute_shap, global_importance, shap_table
from src.model import load_bundle, malignant_proba
from src import visualization as viz

ADDITIVITY_TOL = 1e-6


def describe_case(case: dict, p: float, true_label: int, cmp: dict, lime_res, stab: dict) -> str:
    pred = CLASS_NAMES[int(p >= DECISION_THRESHOLD)]
    correct = "correct" if int(p >= DECISION_THRESHOLD) == true_label else "INCORRECT"
    parts = [
        f"Model predicts {pred} with P(malignant)={p:.3f} (actual: {CLASS_NAMES[true_label]}; {correct}).",
        f"LIME and SHAP share {cmp['top_k_overlap']}/{TOP_K} top features "
        f"(Jaccard {cmp['jaccard_top_k']:.2f}; Spearman rho over |attributions| {cmp['spearman_abs_all_features']:.2f}).",
    ]
    if cmp["direction_disagreements_union"]:
        parts.append("Opposite direction for: " + ", ".join(cmp["direction_disagreements_union"]) + ".")
    else:
        parts.append("No direction disagreement within the top-5 union.")
    parts.append(f"LIME surrogate local fit R^2={lime_res.score:.2f}; top-5 stability across "
                 f"{len(stab['seeds'])} seeds: mean Jaccard {stab['mean_pairwise_jaccard_top_k']:.2f}.")
    return " ".join(parts)


def main() -> None:
    ensure_dirs()
    bundle = load_bundle()
    model, X_train, X_test, y_test = bundle["model"], bundle["X_train"], bundle["X_test"], bundle["y_test"]

    # ------------------------------------------------------------- SHAP (global)
    explainer = build_tree_explainer(model)
    shap_test = compute_shap(explainer, X_test)
    err = additivity_error(model, shap_test, X_test)
    assert err < ADDITIVITY_TOL, f"SHAP additivity violated: {err}"
    print(f"SHAP additivity check on {len(X_test)} test patients: max |error| = {err:.2e}")
    with open(METRICS_DIR / "shap_additivity.json", "w", encoding="utf-8") as f:
        json.dump({"max_abs_error": err, "tolerance": ADDITIVITY_TOL, "n_patients": len(X_test),
                   "base_value_p_malignant": float(shap_test.base_values[0]),
                   "explainer": "shap.TreeExplainer(feature_perturbation='tree_path_dependent')",
                   "output": "P(malignant) — probability units"}, f, indent=2)

    importance = global_importance(shap_test)
    importance.rename("mean_abs_shap").rename_axis("feature").to_csv(METRICS_DIR / "shap_global_importance.csv")
    viz.save(viz.plot_shap_global_bar(importance), FIGURES_DIR / "shap_global_importance.png")
    viz.save(viz.plot_shap_beeswarm(shap_test), FIGURES_DIR / "shap_summary_beeswarm.png")
    plt.close("all")

    # ------------------------------------------------------------- LIME vs SHAP on every test patient
    proba = malignant_proba(model, X_test)
    rows, cache = [], {}
    print(f"Running LIME on {len(X_test)} test patients ...")
    for i, pid in enumerate(X_test.index):
        lime_res = explain_patient_lime(model, X_train, X_test.loc[[pid]])
        shap_vals = pd.Series(shap_test.values[i], index=shap_test.feature_names)
        cmp = compare_explanations(lime_res.weights, shap_vals)
        cache[pid] = (i, lime_res, cmp)
        rows.append({
            "patient_id": int(pid),
            "true_label": int(y_test.loc[pid]),
            "p_malignant": float(proba[i]),
            "predicted_label": int(proba[i] >= DECISION_THRESHOLD),
            "lime_top5": "; ".join(cmp["lime_top_k"]),
            "shap_top5": "; ".join(cmp["shap_top_k"]),
            "top_k_overlap": cmp["top_k_overlap"],
            "jaccard_top_k": cmp["jaccard_top_k"],
            "spearman_abs_all_features": cmp["spearman_abs_all_features"],
            "n_direction_disagreements": len(cmp["direction_disagreements_union"]),
            "lime_local_r2": lime_res.score,
            "lime_local_pred": lime_res.local_pred,
        })
    summary = pd.DataFrame(rows)
    summary.round(4).to_csv(CASE_STUDIES_DIR / "test_set_lime_vs_shap.csv", index=False)

    aggregate = {
        "n_patients": len(summary),
        "mean_top5_jaccard": float(summary["jaccard_top_k"].mean()),
        "mean_top5_overlap": float(summary["top_k_overlap"].mean()),
        "mean_spearman_abs": float(summary["spearman_abs_all_features"].mean()),
        "pct_patients_with_direction_disagreement": float((summary["n_direction_disagreements"] > 0).mean() * 100),
        "mean_lime_local_r2": float(summary["lime_local_r2"].mean()),
    }

    # ------------------------------------------------------------- case studies
    cases = select_case_studies(summary)
    case_rows, case_details = [], []
    for n, case in enumerate(cases, start=1):
        if not case["found"]:
            print(f"Case {n} ({case['case_type']}): NOT FOUND - {case['criterion']}")
            case_rows.append({"case": n, **case})
            case_details.append({"case": n, **case})
            continue
        pid = case["patient_id"]
        i, lime_res, cmp = cache[pid]
        patient = X_test.loc[[pid]]
        stab = lime_stability(model, X_train, patient)
        p = float(proba[i])
        observation = describe_case(case, p, int(y_test.loc[pid]), cmp, lime_res, stab)
        print(f"Case {n} ({case['case_type']}), patient {pid}: {observation}")

        tag = f"case{n}_patient{pid}"
        row_expl = shap_test[i]
        viz.save(viz.plot_lime(lime_res.table, title=f"LIME — patient {pid} ({case['case_type']})"),
                 FIGURES_DIR / f"lime_{tag}.png")
        viz.save(viz.plot_shap_waterfall(row_expl), FIGURES_DIR / f"shap_waterfall_{tag}.png")
        viz.save(viz.plot_shap_force_matplotlib(row_expl), FIGURES_DIR / f"shap_force_{tag}.png")
        (FIGURES_DIR / f"shap_force_{tag}.html").write_text(viz.shap_force_html(row_expl), encoding="utf-8")
        viz.save(viz.plot_lime_vs_shap(cmp["direction_table"],
                                       title=f"LIME vs SHAP — patient {pid} ({case['case_type']})"),
                 FIGURES_DIR / f"lime_vs_shap_{tag}.png")
        plt.close("all")

        case_rows.append({
            "case": n, **case,
            "true_label": CLASS_NAMES[int(y_test.loc[pid])],
            "p_malignant": round(p, 4),
            "predicted": CLASS_NAMES[int(p >= DECISION_THRESHOLD)],
            "lime_top5": "; ".join(cmp["lime_top_k"]),
            "shap_top5": "; ".join(cmp["shap_top_k"]),
            "top_k_overlap": cmp["top_k_overlap"],
            "jaccard_top_k": round(cmp["jaccard_top_k"], 4),
            "spearman_abs_all_features": round(cmp["spearman_abs_all_features"], 4),
            "direction_disagreements": "; ".join(cmp["direction_disagreements_union"]),
            "lime_local_r2": round(lime_res.score, 4),
            "lime_stability_mean_jaccard": round(stab["mean_pairwise_jaccard_top_k"], 4),
            "lime_features_with_sign_flip_across_seeds": stab["features_with_sign_flip"],
            "observation": observation,
        })
        case_details.append({
            "case": n, **case,
            "true_label": CLASS_NAMES[int(y_test.loc[pid])],
            "p_malignant": p,
            "shap_base_value": float(row_expl.base_values),
            "shap_sum": float(row_expl.values.sum()),
            "lime_intercept": lime_res.intercept,
            "lime_local_pred": lime_res.local_pred,
            "lime_local_r2": lime_res.score,
            "comparison": {k: v for k, v in cmp.items() if k != "direction_table"},
            "direction_table": cmp["direction_table"].round(5).to_dict(orient="records"),
            "lime_top10": lime_res.table.head(10)[["feature", "rule", "weight"]].round(5).to_dict(orient="records"),
            "shap_top10": shap_table(row_expl).head(10)[["feature", "value", "shap_value"]].round(5)
            .to_dict(orient="records"),
            "lime_stability": {k: v for k, v in stab.items() if k not in ("weight_mean", "weight_std")},
            "observation": observation,
        })

    case_df = pd.DataFrame(case_rows)
    case_df.to_csv(CASE_STUDIES_DIR / "case_studies.csv", index=False)
    with open(CASE_STUDIES_DIR / "case_studies.json", "w", encoding="utf-8") as f:
        json.dump({"aggregate_test_set": aggregate, "cases": case_details}, f, indent=2, default=float)
    viz.save(viz.plot_case_study_overview(case_df), FIGURES_DIR / "case_study_agreement.png")
    viz.save(viz.plot_architecture(), FIGURES_DIR / "architecture.png")
    plt.close("all")

    print("\nAggregate LIME vs SHAP agreement over the test set:")
    for k, v in aggregate.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")
    print(f"\nOutputs written to {FIGURES_DIR.parent}")


if __name__ == "__main__":
    main()
