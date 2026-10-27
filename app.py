"""ClinXAI — Transparent Clinical Diagnostics (Streamlit dashboard).

Run:  streamlit run app.py
Research / educational demonstration only. Not a medical device; no clinical recommendations.
"""
import json
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src.comparison import compare_explanations, lime_stability
from src.config import (
    CASE_STUDIES_DIR,
    CLASS_NAMES,
    DECISION_THRESHOLD,
    FIGURES_DIR,
    LIME_NUM_SAMPLES,
    METRICS_DIR,
    MODEL_PATH,
    RANDOM_STATE,
    TOP_K,
)
from src.data_loader import out_of_range_features, validate_patient_input
from src.explain_lime import explain_patient_lime
from src.explain_shap import additivity_error, build_tree_explainer, compute_shap, global_importance, shap_table
from src.model import load_bundle, malignant_proba, roc_points
from src import visualization as viz

warnings.filterwarnings("ignore")
st.set_page_config(page_title="ClinXAI — Transparent Clinical Diagnostics", page_icon="🩺", layout="wide")

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.6rem; max-width: 1350px;}
      .cx-banner {background: linear-gradient(90deg,#0B7A75 0%,#1E6FB8 100%); color:#fff;
                  padding: 18px 24px; border-radius: 12px; margin-bottom: 10px;}
      .cx-banner h1 {color:#fff; margin:0; font-size: 1.9rem;}
      .cx-banner p {margin: 4px 0 0 0; opacity: .92;}
      .cx-disclaimer {background:#FFF7E6; border-left: 5px solid #D98E04; padding: 10px 14px;
                      border-radius: 6px; font-size: .92rem; color:#5B3B00;}
      .cx-pred {border-radius: 12px; padding: 16px 20px; color: #fff; font-size: 1.25rem; font-weight: 700;}
      .cx-mal {background:#C8102E;} .cx-ben {background:#1E6FB8;}
      div[data-testid="stMetricValue"] {font-size: 1.6rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

DISCLAIMER = (
    "⚠️ <b>Research / educational demonstration only.</b> ClinXAI is not a medical device, has not been "
    "clinically validated, and must not be used for diagnosis or treatment decisions."
)


# ------------------------------------------------------------------ cached resources
@st.cache_resource(show_spinner="Loading model and computing SHAP values …")
def load_resources():
    if not MODEL_PATH.exists():
        import train_model
        train_model.main()
    bundle = load_bundle()
    explainer = build_tree_explainer(bundle["model"])
    shap_test = compute_shap(explainer, bundle["X_test"])
    return {
        **bundle,
        "explainer": explainer,
        "shap_test": shap_test,
        "importance": global_importance(shap_test),
        "proba_test": malignant_proba(bundle["model"], bundle["X_test"]),
        "additivity_error": additivity_error(bundle["model"], shap_test, bundle["X_test"]),
    }


@st.cache_data(show_spinner="Running LIME (local perturbations) …", max_entries=64)
def cached_lime(values: tuple, seed: int, num_samples: int):
    R = load_resources()
    patient = pd.DataFrame([values], columns=R["feature_names"])
    return explain_patient_lime(R["model"], R["X_train"], patient, seed=seed, num_samples=num_samples)


@st.cache_data(max_entries=64)
def cached_shap(values: tuple):
    R = load_resources()
    patient = pd.DataFrame([values], columns=R["feature_names"])
    return compute_shap(R["explainer"], patient)[0]


@st.cache_data(show_spinner="Re-running LIME with 5 different seeds …", max_entries=16)
def cached_stability(values: tuple, num_samples: int):
    R = load_resources()
    patient = pd.DataFrame([values], columns=R["feature_names"])
    return lime_stability(R["model"], R["X_train"], patient, num_samples=num_samples)


@st.cache_data
def load_case_studies():
    path_csv, path_json = CASE_STUDIES_DIR / "case_studies.csv", CASE_STUDIES_DIR / "case_studies.json"
    if not path_csv.exists() or not path_json.exists():
        return None, None
    with open(path_json, encoding="utf-8") as f:
        return pd.read_csv(path_csv), json.load(f)


def show(fig):
    st.pyplot(fig, clear_figure=True, width="stretch")
    plt.close(fig)


R = load_resources()
model, X_train, X_test, y_test = R["model"], R["X_train"], R["X_test"], R["y_test"]
features = R["feature_names"]
case_df, case_json = load_case_studies()
case_lookup = {}
if case_df is not None:
    for _, r in case_df[case_df["found"]].iterrows():
        case_lookup[int(r["patient_id"])] = r["case_type"]

# ------------------------------------------------------------------ sidebar
st.sidebar.markdown("### 🩺 ClinXAI")
st.sidebar.caption("Select a held-out test patient. Every tab updates for the selected patient.")
patient_ids = [int(i) for i in X_test.index]
if "patient_id" not in st.session_state:
    st.session_state["patient_id"] = next(iter(case_lookup), patient_ids[0])


def patient_label(pid: int) -> str:
    i = patient_ids.index(pid)
    tag = f"  ★ {case_lookup[pid]}" if pid in case_lookup else ""
    return f"Patient #{pid} — actual {CLASS_NAMES[int(y_test.loc[pid])]}, P={R['proba_test'][i]:.2f}{tag}"


pid = st.sidebar.selectbox("Test patient", patient_ids, format_func=patient_label, key="patient_id")
st.sidebar.markdown("---")
st.sidebar.markdown("**LIME settings**")
lime_seed = int(st.sidebar.number_input("Random seed", min_value=0, max_value=10_000, value=RANDOM_STATE, step=1))
lime_samples = int(st.sidebar.select_slider("Perturbation samples", [1000, 2000, 5000, 10000],
                                            value=LIME_NUM_SAMPLES))
st.sidebar.caption("Seed 42 with 5000 samples reproduces the saved case-study outputs exactly.")
st.sidebar.markdown("---")
st.sidebar.markdown(f"<div class='cx-disclaimer'>{DISCLAIMER}</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------ header
st.markdown(
    "<div class='cx-banner'><h1>ClinXAI — Transparent Clinical Diagnostics</h1>"
    "<p>Random Forest diagnosis of breast-tumour biopsies, explained locally with LIME and locally + globally "
    "with SHAP</p></div>",
    unsafe_allow_html=True,
)

tabs = st.tabs(["Overview", "Diagnostic Prediction", "LIME Explanation", "SHAP Explanation",
                "LIME vs SHAP", "Model Evaluation", "Case Studies"])

# ------------------------------------------------------------------ A. Overview
with tabs[0]:
    c1, c2 = st.columns([1.35, 1])
    with c1:
        st.subheader("Objective")
        st.markdown(
            "Build an end-to-end clinical diagnostic prediction system with a complex tree ensemble "
            "(**Random Forest**) and make every prediction transparent with two complementary explainers:\n"
            "- **LIME** — fits a simple weighted linear *surrogate* around one patient using random perturbations.\n"
            "- **SHAP** — game-theoretic *Shapley values* that split the prediction exactly among the features "
            "(local), and aggregate over patients (global).\n\n"
            "The project then studies **when the two explanations disagree**, which matters most on borderline "
            "and misclassified patients."
        )
        st.subheader("Dataset")
        meta = R["metrics"]["dataset"]
        st.markdown(
            f"**Breast Cancer Wisconsin (Diagnostic)** via `sklearn.datasets.load_breast_cancer()` — "
            f"{meta['n_samples']} patients × {meta['n_features']} numeric features computed from digitised images "
            "of fine-needle-aspirate cell nuclei (radius, texture, perimeter, area, smoothness, compactness, "
            "concavity, concave points, symmetry, fractal dimension; each as *mean*, *standard error* and *worst*).\n\n"
            f"- Class encoding used throughout the app: **Malignant = 1 (positive / risk class)**, Benign = 0 "
            f"(sklearn's raw encoding is the reverse and is re-mapped on load).\n"
            f"- {meta['n_malignant']} malignant, {meta['n_benign']} benign. "
            f"Stratified 80/20 split → {meta['n_train']} train / {meta['n_test']} held-out test patients."
        )
        st.info(
            "**Scope note.** The inputs are *structured tabular features* derived from images — the app does not "
            "process raw images. 'Multi-modal' here refers to two complementary explanation modalities "
            "(LIME and SHAP). True image + tabular fusion is future scope."
        )
    with c2:
        st.subheader("Workflow")
        arch = FIGURES_DIR / "architecture.png"
        if arch.exists():
            st.image(str(arch), width="stretch")
        st.markdown(
            "1. Load & validate data, re-encode malignant = 1\n"
            "2. Stratified split (seed 42) — all fitting on training data only\n"
            "3. Train Random Forest (+ Logistic Regression baseline)\n"
            "4. Predict P(malignant) for a held-out patient\n"
            "5. Explain with LIME and SHAP (same patient, same class)\n"
            "6. Compare rankings & directions; evaluate case studies"
        )
    st.markdown(f"<div class='cx-disclaimer'>{DISCLAIMER}</div>", unsafe_allow_html=True)

# ------------------------------------------------------------------ B. Diagnostic prediction
with tabs[1]:
    base_row = X_test.loc[pid]
    st.subheader(f"Patient #{pid}")
    st.caption(f"Recorded diagnosis (ground truth, hidden from the model): **{CLASS_NAMES[int(y_test.loc[pid])]}**"
               + (f" · Case study: **{case_lookup[pid]}**" if pid in case_lookup else ""))

    adjust = st.toggle("Adjust biomarker values (what-if analysis)", value=False, key=f"adj_on_{pid}")
    values = base_row.copy()
    if adjust:
        top_feats = list(R["importance"].index[:8])
        st.caption("Editing the 8 globally most important features (by mean |SHAP|). All explanations in the "
                   "other tabs use these adjusted values.")
        cols = st.columns(4)
        for j, f in enumerate(top_feats):
            lo, hi = float(X_train[f].min()), float(X_train[f].max())
            values[f] = cols[j % 4].number_input(
                f, min_value=0.0, value=float(base_row[f]), format="%.4f", key=f"adj_{pid}_{f}",
                help=f"Training range: {lo:.4g} – {hi:.4g}",
            )

    try:
        patient = validate_patient_input(values.to_dict(), features)
    except ValueError as exc:
        st.error(f"Invalid biomarker input: {exc}")
        st.stop()
    oor = out_of_range_features(patient, X_train)
    if oor:
        st.warning("Outside the training data range (model is extrapolating; explanations are less reliable): "
                   + ", ".join(oor))
    values_t = tuple(float(v) for v in patient.iloc[0].to_numpy())
    p = float(malignant_proba(model, patient)[0])
    pred = int(p >= DECISION_THRESHOLD)

    c1, c2 = st.columns([1, 2.2])
    with c1:
        css = "cx-mal" if pred else "cx-ben"
        st.markdown(f"<div class='cx-pred {css}'>Model output: {CLASS_NAMES[pred]}</div>", unsafe_allow_html=True)
        st.metric("P(malignant)", f"{p:.3f}")
        st.metric("P(benign)", f"{1 - p:.3f}")
        st.caption(f"Decision threshold {DECISION_THRESHOLD}. The probability is the fraction of tree votes — an "
                   "**uncalibrated** model score, not a calibrated clinical risk.")
    with c2:
        show(viz.plot_risk_gauge(p, DECISION_THRESHOLD))
        conf = abs(p - 0.5)
        if conf < 0.15:
            st.warning("Borderline output: the trees are split. Explanations for such patients tend to be less "
                       "stable — see the LIME vs SHAP tab.")
    with st.expander("All 30 biomarker values for this patient"):
        tbl = pd.DataFrame({"value": patient.iloc[0], "train min": X_train.min(), "train median": X_train.median(),
                            "train max": X_train.max()})
        st.dataframe(tbl.style.format("{:.4f}"), width="stretch", height=420)

lime_res = cached_lime(values_t, lime_seed, lime_samples)
shap_row = cached_shap(values_t)
shap_series = pd.Series(shap_row.values, index=features)
cmp = compare_explanations(lime_res.weights, shap_series, TOP_K)
adj_note = " (adjusted values)" if adjust else ""

# ------------------------------------------------------------------ C. LIME
with tabs[2]:
    st.subheader(f"LIME local explanation — Patient #{pid}{adj_note}")
    c1, c2 = st.columns([1.6, 1])
    with c1:
        show(viz.plot_lime(lime_res.table, n=10))
    with c2:
        m1, m2 = st.columns(2)
        m1.metric("Random Forest P(malignant)", f"{lime_res.model_proba:.3f}")
        m2.metric("Surrogate prediction", f"{lime_res.local_pred:.3f}")
        m1.metric("Surrogate intercept", f"{lime_res.intercept:.3f}")
        m2.metric("Local fit R²", f"{lime_res.score:.2f}")
        st.markdown(
            "**How to read this chart.** LIME generated "
            f"{lime_samples:,} perturbed versions of this patient (sampled from training-data statistics), asked "
            "the Random Forest for P(malignant) on each, and fitted a proximity-weighted linear model. Each bar "
            "is that surrogate's weight for a feature *condition* (e.g. `worst area > 1122.50`). "
            "**Red** pushes toward malignant, **blue** toward benign."
        )
        if lime_res.score < 0.3:
            st.warning(f"Local fit R² = {lime_res.score:.2f}: the linear surrogate explains little of the model's "
                       "local behaviour, so treat these weights with caution.")
    st.markdown("**Most influential conditions (top 10)**")
    st.dataframe(lime_res.table.head(10)[["rank", "rule", "weight", "direction"]].style.format({"weight": "{:+.4f}"}),
                 width="stretch", hide_index=True)
    st.caption(f"Seed {lime_seed}, {lime_samples} samples, quartile discretisation, explainer fitted on training "
               "data only. Change the seed in the sidebar to see LIME's sensitivity to random perturbations.")

# ------------------------------------------------------------------ D. SHAP
with tabs[3]:
    st.subheader("Global explanations (held-out test set, 114 patients)")
    g1, g2 = st.columns(2)
    with g1:
        show(viz.plot_shap_global_bar(R["importance"]))
        st.caption("Mean |SHAP| — the average absolute change in P(malignant) attributed to each feature.")
    with g2:
        show(viz.plot_shap_beeswarm(R["shap_test"]))
        st.caption("Each dot is a patient. Position = effect on P(malignant); colour = feature value (red high).")

    st.markdown("---")
    st.subheader(f"Local explanation — Patient #{pid}{adj_note}")
    base_v = float(shap_row.base_values)
    s1, s2, s3 = st.columns(3)
    s1.metric("Base value E[f(x)]", f"{base_v:.3f}")
    s2.metric("Sum of SHAP values", f"{shap_row.values.sum():+.3f}")
    s3.metric("Base + sum = P(malignant)", f"{base_v + shap_row.values.sum():.3f}",
              help=f"Model predict_proba: {p:.3f}")
    l1, l2 = st.columns([1.15, 1])
    with l1:
        show(viz.plot_shap_waterfall(shap_row))
    with l2:
        tbl = shap_table(shap_row)
        st.markdown("**Feature contribution table**")
        st.dataframe(tbl[["rank", "feature", "value", "shap_value", "direction"]]
                     .style.format({"value": "{:.4f}", "shap_value": "{:+.4f}"})
                     .map(lambda v: "color:#C8102E" if v == "→ Malignant" else "color:#1E6FB8", subset=["direction"]),
                     width="stretch", hide_index=True, height=440)
    st.markdown("**Force plot**")
    show(viz.plot_shap_force_matplotlib(shap_row))
    with st.expander("Interactive force plot (SHAP JavaScript)"):
        try:
            force_html = viz.shap_force_html(shap_row)  # generated locally by SHAP, not user content
            if hasattr(st, "iframe"):
                st.iframe(force_html, height=180)
            else:  # older Streamlit
                components.html(force_html, height=180, scrolling=True)
        except Exception as exc:  # JS bundle unavailable in this SHAP version
            st.info(f"Interactive force plot unavailable ({exc}); the static version above is equivalent.")
    st.caption("TreeExplainer (tree-path-dependent) on the Random Forest's probability output. SHAP values, the base "
               f"value and predict_proba share probability units; max additivity error on the test set = "
               f"{R['additivity_error']:.1e}.")

# ------------------------------------------------------------------ E. LIME vs SHAP
with tabs[4]:
    st.subheader(f"LIME vs SHAP — Patient #{pid}{adj_note}")
    st.caption("Same patient · same trained Random Forest · same target: P(malignant).")
    m = st.columns(4)
    m[0].metric(f"Top-{TOP_K} overlap", f"{cmp['top_k_overlap']} / {TOP_K}")
    m[1].metric(f"Top-{TOP_K} Jaccard", f"{cmp['jaccard_top_k']:.2f}")
    m[2].metric("Spearman ρ (|attr|, 30 features)", f"{cmp['spearman_abs_all_features']:.2f}")
    dis = cmp["direction_disagreements_union"]
    m[3].metric("Direction disagreements", f"{len(dis)}", help="Features in the union of both top-5 lists whose "
                "LIME weight and SHAP value have opposite sign.")
    show(viz.plot_lime_vs_shap(cmp["direction_table"]))

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**LIME top-{TOP_K}**")
        st.dataframe(lime_res.table.head(TOP_K)[["rank", "feature", "rule", "weight"]]
                     .style.format({"weight": "{:+.4f}"}), width="stretch", hide_index=True)
    with c2:
        st.markdown(f"**SHAP top-{TOP_K}**")
        st.dataframe(shap_table(shap_row).head(TOP_K)[["rank", "feature", "value", "shap_value"]]
                     .style.format({"value": "{:.4f}", "shap_value": "{:+.4f}"}), width="stretch", hide_index=True)

    st.markdown("**Ranking & direction table** (union of both top-5 lists)")
    dt = cmp["direction_table"].copy()
    dt["agreement"] = np.where(dt["same_direction"], "✓ same direction", "⚠ opposite")
    st.dataframe(dt[["feature", "lime_rank", "shap_rank", "lime_weight", "shap_value", "agreement"]]
                 .style.format({"lime_weight": "{:+.4f}", "shap_value": "{:+.4f}"}), width="stretch", hide_index=True)

    if dis:
        st.warning("Opposite direction for: **" + ", ".join(dis) + "**")
    else:
        st.success("LIME and SHAP agree on the direction of every feature in the top-5 union.")

    if st.toggle("Measure LIME stability across 5 random seeds", value=False, key="stab"):
        stab = cached_stability(values_t, lime_samples)
        s = st.columns(3)
        s[0].metric("Mean pairwise top-5 Jaccard", f"{stab['mean_pairwise_jaccard_top_k']:.2f}")
        s[1].metric("Worst-case top-5 Jaccard", f"{stab['min_pairwise_jaccard_top_k']:.2f}")
        s[2].metric("Features whose sign flips", f"{stab['features_with_sign_flip']} / 30")
        st.caption("SHAP TreeExplainer is deterministic for a fixed model, so its stability is 1.00 by construction.")

    st.markdown("#### Why can the explanations differ?")
    reasons = [
        "**Different questions.** LIME fits a linear surrogate over *discretised* feature bins in a sampled "
        "neighbourhood; SHAP distributes the exact prediction using Shapley values along the trees' own splits. "
        "Their magnitudes are not interchangeable — only ranks and signs are compared here.",
        "**Correlated features.** Radius, perimeter and area (mean/worst) are almost collinear. Both methods may "
        "share credit among them differently, so a feature can rank high in one and low in the other.",
        "**Perturbation sampling.** LIME's samples are drawn independently per feature, creating unrealistic "
        "combinations (e.g. large radius with small area) that the forest never saw.",
    ]
    if lime_res.score < 0.3:
        reasons.append(f"**Weak local fit for this patient** — LIME R² = {lime_res.score:.2f}, so the surrogate "
                       "is a poor approximation here.")
    if abs(p - 0.5) < 0.25:
        reasons.append(f"**Near the decision boundary** (P = {p:.2f}): the forest's response is non-linear here, "
                       "which a single linear surrogate cannot capture.")
    st.markdown("\n".join(f"- {r}" for r in reasons))
    st.caption("Jaccard and Spearman measure agreement between explanation methods — they are not clinical "
               "validation metrics.")

# ------------------------------------------------------------------ F. Model evaluation
with tabs[5]:
    rf_m, lr_m = R["metrics"]["random_forest"], R["metrics"]["logistic_regression_baseline"]
    st.subheader("Random Forest — held-out test set")
    st.caption(f"Positive class: **{rf_m['positive_class']}** · threshold {rf_m['decision_threshold']} · "
               f"{R['metrics']['dataset']['split']}")
    m = st.columns(6)
    for col, (name, key) in zip(m, [("Accuracy", "accuracy"), ("Precision", "precision"),
                                    ("Recall (sensitivity)", "recall_sensitivity"), ("Specificity", "specificity"),
                                    ("F1-score", "f1"), ("ROC-AUC", "roc_auc")]):
        col.metric(name, f"{rf_m[key]:.4f}")
    c1, c2 = st.columns(2)
    with c1:
        show(viz.plot_confusion_matrix(rf_m["confusion_matrix"], "Random Forest — confusion matrix (test set)"))
    with c2:
        curves = {
            "Random Forest": (*roc_points(model, X_test, y_test), rf_m["roc_auc"]),
            "Logistic Regression": (*roc_points(R["baseline"], X_test, y_test), lr_m["roc_auc"]),
        }
        show(viz.plot_roc(curves))
    st.markdown("**Comparison with interpretable baseline**")
    cols = ["accuracy", "precision", "recall_sensitivity", "specificity", "f1", "roc_auc"]
    st.dataframe(pd.DataFrame({"Random Forest": [rf_m[c] for c in cols],
                               "Logistic Regression (baseline)": [lr_m[c] for c in cols]}, index=cols)
                 .style.format("{:.4f}"), width="stretch")
    d = R["metrics"]["dataset"]
    st.markdown(
        f"- Training set: **{d['n_train']}** patients · Test set: **{d['n_test']}** patients "
        f"({d['test_malignant']} malignant / {d['test_benign']} benign)\n"
        f"- Random Forest: {rf_m['params']['n_estimators']} trees, random_state {rf_m['params']['random_state']}\n"
        f"- 5-fold stratified CV ROC-AUC on the training set: **{rf_m['cv_roc_auc_mean']:.4f} ± "
        f"{rf_m['cv_roc_auc_std']:.4f}**\n"
        f"- False negatives (malignant predicted benign): **{rf_m['confusion_matrix']['fn']}** — the clinically "
        "most costly error type; examined in the Case Studies tab."
    )
    st.caption("A single 114-patient test split is small; metrics would vary with a different split.")

# ------------------------------------------------------------------ G. Case studies
with tabs[6]:
    st.subheader("Reproducible case studies (selected programmatically from the held-out test set)")
    if case_df is None:
        st.info("Case-study outputs not found. Run `python evaluate.py` to generate them.")
    else:
        agg = case_json["aggregate_test_set"]
        a = st.columns(4)
        a[0].metric("Mean top-5 Jaccard (114 patients)", f"{agg['mean_top5_jaccard']:.2f}")
        a[1].metric("Mean top-5 overlap", f"{agg['mean_top5_overlap']:.2f} / 5")
        a[2].metric("Mean Spearman ρ", f"{agg['mean_spearman_abs']:.2f}")
        a[3].metric("Patients with a direction disagreement", f"{agg['pct_patients_with_direction_disagreement']:.1f}%")
        ov = FIGURES_DIR / "case_study_agreement.png"
        if ov.exists():
            st.image(str(ov), width="stretch")

        def jump(target):
            st.session_state["patient_id"] = target

        for case in case_json["cases"]:
            title = f"Case {case['case']}: {case['case_type']}"
            if not case["found"]:
                with st.expander(title + " — not found"):
                    st.info(case["criterion"])
                continue
            cpid = case["patient_id"]
            with st.expander(f"{title} — Patient #{cpid} · P(malignant) = {case['p_malignant']:.3f} · "
                             f"actual {case['true_label']}", expanded=case["case"] == 3):
                st.caption(f"Selection rule: {case['criterion']}")
                st.markdown(f"**Observation.** {case['observation']}")
                c = case["comparison"]
                k = st.columns(4)
                k[0].metric("Top-5 overlap", f"{c['top_k_overlap']} / 5")
                k[1].metric("Spearman ρ", f"{c['spearman_abs_all_features']:.2f}")
                k[2].metric("LIME local R²", f"{case['lime_local_r2']:.2f}")
                k[3].metric("LIME seed stability", f"{case['lime_stability']['mean_pairwise_jaccard_top_k']:.2f}")
                tag = f"case{case['case']}_patient{cpid}"
                img = FIGURES_DIR / f"lime_vs_shap_{tag}.png"
                if img.exists():
                    st.image(str(img), width="stretch")
                st.button(f"Open patient #{cpid} in all tabs", key=f"jump_{cpid}", on_click=jump, args=(cpid,))

        st.markdown("#### Engineering limitations")
        st.markdown(
            "- **Uncalibrated probabilities** — Random Forest vote fractions; no calibration was fitted.\n"
            "- **Small, single-centre dataset** (569 patients); a single 80/20 split; no external validation.\n"
            "- **LIME instability** — results depend on the random seed and number of samples, and its local fit "
            "R² is often low (mean over test set reported above).\n"
            "- **LIME vs SHAP semantics differ** — surrogate coefficients vs Shapley attributions; only ranks and "
            "signs are compared, never magnitudes.\n"
            "- **Correlated features** (radius/perimeter/area) split credit unpredictably in both methods.\n"
            "- **Tree-path-dependent SHAP** reflects the model's learned structure, not causal effects.\n"
            "- **Tabular only** — features derived from images; no raw-image modality."
        )
    st.markdown(f"<div class='cx-disclaimer'>{DISCLAIMER}</div>", unsafe_allow_html=True)
