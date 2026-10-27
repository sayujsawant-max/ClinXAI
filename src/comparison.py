"""LIME vs SHAP comparison measures and programmatic case-study selection.

These are measures of agreement *between explanation methods*; they say nothing about clinical
validity. LIME weights are coefficients of a local weighted linear surrogate over discretised
feature bins, while SHAP values are additive Shapley attributions in probability units, so only
ranks and signs are compared - never raw magnitudes.
"""
from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from src.config import LIME_STABILITY_SEEDS, TOP_K
from src.explain_lime import explain_patient_lime


def top_k(weights: pd.Series, k: int = TOP_K) -> list[str]:
    return list(weights.abs().sort_values(ascending=False, kind="mergesort").index[:k])


def jaccard(a, b) -> float:
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 1.0


def compare_explanations(lime_weights: pd.Series, shap_values: pd.Series, k: int = TOP_K) -> dict:
    """Compare two attribution vectors indexed by the same feature names (same patient, class)."""
    lime_weights = lime_weights.reindex(shap_values.index).fillna(0.0)
    lime_top, shap_top = top_k(lime_weights, k), top_k(shap_values, k)
    shared = [f for f in lime_top if f in shap_top]
    union = list(dict.fromkeys(lime_top + shap_top))

    rho, _ = spearmanr(lime_weights.abs().to_numpy(), shap_values.abs().to_numpy())

    direction_rows = []
    for f in union:
        lw, sv = float(lime_weights[f]), float(shap_values[f])
        direction_rows.append(
            {
                "feature": f,
                "lime_weight": lw,
                "shap_value": sv,
                "lime_rank": int(lime_weights.abs().rank(ascending=False, method="first")[f]),
                "shap_rank": int(shap_values.abs().rank(ascending=False, method="first")[f]),
                "in_lime_top_k": f in lime_top,
                "in_shap_top_k": f in shap_top,
                "same_direction": bool(np.sign(lw) == np.sign(sv)),
            }
        )
    direction_df = pd.DataFrame(direction_rows)
    disagreements = direction_df.loc[~direction_df["same_direction"], "feature"].tolist()
    shared_df = direction_df[direction_df["feature"].isin(shared)]
    return {
        "k": k,
        "lime_top_k": lime_top,
        "shap_top_k": shap_top,
        "shared_top_k": shared,
        "top_k_overlap": len(shared),
        "jaccard_top_k": jaccard(lime_top, shap_top),
        "spearman_abs_all_features": float(rho) if np.isfinite(rho) else float("nan"),
        "direction_agreement_shared": float(shared_df["same_direction"].mean()) if len(shared_df) else float("nan"),
        "direction_disagreements_union": disagreements,
        "direction_table": direction_df,
    }


def lime_stability(model, X_train: pd.DataFrame, patient, seeds=LIME_STABILITY_SEEDS, k: int = TOP_K,
                   num_samples: int | None = None) -> dict:
    """Re-run LIME with different random seeds and measure how much the top-k set changes."""
    kwargs = {"num_samples": num_samples} if num_samples else {}
    runs = [explain_patient_lime(model, X_train, patient, seed=s, **kwargs) for s in seeds]
    tops = [top_k(r.weights, k) for r in runs]
    pair_j = [jaccard(a, b) for a, b in combinations(tops, 2)]
    W = pd.DataFrame({s: r.weights for s, r in zip(seeds, runs)})
    sign_flip = (np.sign(W).nunique(axis=1) > 1)
    return {
        "seeds": list(seeds),
        "mean_pairwise_jaccard_top_k": float(np.mean(pair_j)),
        "min_pairwise_jaccard_top_k": float(np.min(pair_j)),
        "features_with_sign_flip": int(sign_flip.sum()),
        "weight_mean": W.mean(axis=1),
        "weight_std": W.std(axis=1),
    }


def select_case_studies(summary: pd.DataFrame) -> list[dict]:
    """Pick cases from the per-patient test summary.

    `summary` needs columns: patient_id, p_malignant, jaccard_top_k, spearman_abs_all_features,
    n_direction_disagreements. Ties are broken by patient_id for reproducibility.
    """
    s = summary.sort_values("patient_id").reset_index(drop=True)
    cases, used = [], set()

    def add(case_type, row, criterion):
        used.add(int(row["patient_id"]))
        cases.append({"case_type": case_type, "patient_id": int(row["patient_id"]), "criterion": criterion,
                      "found": True})

    def avail():
        return s[~s["patient_id"].isin(used)]

    add("Clearly malignant", avail().sort_values("p_malignant", ascending=False, kind="mergesort").iloc[0],
        "Highest predicted P(malignant) on the held-out test set")
    add("Clearly benign", avail().sort_values("p_malignant", ascending=True, kind="mergesort").iloc[0],
        "Lowest predicted P(malignant) on the held-out test set")
    border = avail().assign(dist=lambda d: (d["p_malignant"] - 0.5).abs())
    add("Borderline", border.sort_values("dist", kind="mergesort").iloc[0],
        "Predicted P(malignant) closest to the 0.5 decision threshold")

    div = avail().sort_values(["jaccard_top_k", "spearman_abs_all_features"], kind="mergesort").iloc[0]
    add("Ranking divergence", div, "Lowest top-5 Jaccard overlap between LIME and SHAP (ties: lowest Spearman)")

    dirs = avail().sort_values(["n_direction_disagreements", "jaccard_top_k"], ascending=[False, True],
                               kind="mergesort")
    if len(dirs) and dirs.iloc[0]["n_direction_disagreements"] > 0:
        add("Direction disagreement", dirs.iloc[0],
            "Most features (within the union of both top-5 lists) with opposite LIME/SHAP sign")
    else:
        cases.append({"case_type": "Direction disagreement", "patient_id": None, "found": False,
                      "criterion": "No test patient had a LIME/SHAP sign disagreement within the top-5 union"})
    return cases
