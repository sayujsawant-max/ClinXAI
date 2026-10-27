"""Report-only figures for the ClinXAI micro-project report.

Reads the dataset and the already-generated outputs; it does not retrain, re-explain or modify anything
under models/ or outputs/. Run from the project root:  python report/make_report_figures.py
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.data_loader import load_dataset, split_data  # noqa: E402
from src.visualization import ACCENT, BENIGN_COLOR, INK, MALIGNANT_COLOR  # noqa: E402

OUT = ROOT / "report" / "figures"
OUT.mkdir(parents=True, exist_ok=True)


def save(fig, name):
    fig.savefig(OUT / name, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", name)


# ------------------------------------------------------------------ dataset distribution
X, y, _ = load_dataset()
split = split_data(X, y)
fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
groups = [("All (569)", y), ("Train (455)", split.y_train), ("Test (114)", split.y_test)]
xs = np.arange(len(groups))
mal = [int(g.sum()) for _, g in groups]
ben = [int((g == 0).sum()) for _, g in groups]
axes[0].bar(xs - 0.2, ben, 0.4, color=BENIGN_COLOR, label="Benign (0)")
axes[0].bar(xs + 0.2, mal, 0.4, color=MALIGNANT_COLOR, label="Malignant (1)")
for i in range(len(groups)):
    axes[0].text(xs[i] - 0.2, ben[i] + 4, str(ben[i]), ha="center", fontsize=8)
    axes[0].text(xs[i] + 0.2, mal[i] + 4, str(mal[i]), ha="center", fontsize=8)
axes[0].set_xticks(xs, [g for g, _ in groups])
axes[0].set_ylabel("Patients")
axes[0].set_title("(a) Class balance and stratified split", fontsize=10, fontweight="bold")
axes[0].legend(frameon=False, fontsize=8)
for ax, feat, tag in [(axes[1], "worst area", "(b)"), (axes[2], "mean concave points", "(c)")]:
    bins = np.linspace(X[feat].min(), X[feat].max(), 30)
    ax.hist(X.loc[y == 0, feat], bins=bins, alpha=0.65, color=BENIGN_COLOR, label="Benign")
    ax.hist(X.loc[y == 1, feat], bins=bins, alpha=0.65, color=MALIGNANT_COLOR, label="Malignant")
    ax.set_xlabel(feat)
    ax.set_ylabel("Patients")
    ax.set_title(f"{tag} Distribution of '{feat}' by class", fontsize=10, fontweight="bold")
    ax.legend(frameon=False, fontsize=8)
for ax in axes:
    ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
save(fig, "report_dataset_distribution.png")


# ------------------------------------------------------------------ diagram helpers
def box(ax, x, y, w, h, text, fc, fs=8.5, ec=INK, style="round,pad=0.04,rounding_size=0.12"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=style, fc=fc, ec=ec, lw=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=INK)


def arrow(ax, x1, y1, x2, y2, label=None, lx=0, ly=0.12):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", color=INK, lw=1.2))
    if label:
        ax.text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label, ha="center", fontsize=7, color="#475467",
                style="italic")


# ------------------------------------------------------------------ data-flow diagram (actual files)
fig, ax = plt.subplots(figsize=(13, 6.2))
ax.set_xlim(0, 13); ax.set_ylim(0, 6.2); ax.axis("off")
PROC, STORE, EXT = "#E6F4F1", "#F3F4F6", "#E8F1FA"
box(ax, 0.2, 2.75, 2.0, 0.9, "sklearn\nload_breast_cancer()", EXT)
box(ax, 2.9, 2.75, 2.2, 0.9, "P1  train_model.py\nload · re-encode · split\ntrain RF + LR · evaluate", PROC)
box(ax, 2.9, 4.6, 2.2, 0.85, "P4  tests/test_pipeline.py\n24 pytest checks", PROC)
box(ax, 2.9, 0.4, 2.2, 0.95, "D2  outputs/metrics/\nmetrics.json · metrics.csv\ndataset_overview.csv", STORE,
    style="square,pad=0.04")
box(ax, 5.8, 4.6, 2.5, 0.85, "D1  models/\nclinxai_rf_bundle.joblib", STORE, style="square,pad=0.04")
box(ax, 5.8, 2.75, 2.5, 0.9, "P3  app.py (Streamlit)\nlive LIME / SHAP for the\nselected or edited patient", PROC)
box(ax, 5.8, 0.4, 2.5, 0.95, "User (student /\nfaculty viewer)", EXT)
box(ax, 9.0, 4.6, 2.3, 0.85, "P2  evaluate.py\nSHAP · LIME (114 patients)\ncomparison · cases", PROC)
box(ax, 9.0, 2.75, 3.8, 0.95, "D3  outputs/figures/ · outputs/case_studies/\nPNG + HTML figures · case_studies.csv/json\n"
    "test_set_lime_vs_shap.csv · shap_additivity.json", STORE, style="square,pad=0.04")
arrow(ax, 2.2, 3.2, 2.9, 3.2, "569 × 30 features")
arrow(ax, 4.0, 4.6, 4.0, 3.65, "verifies src/ and app", lx=-0.85, ly=0.0)
arrow(ax, 4.0, 2.75, 4.0, 1.35, "metrics, CM, ROC", lx=0.65, ly=0.0)
arrow(ax, 5.1, 3.45, 5.8, 4.85, "model + split\n+ metrics", lx=-0.45, ly=0.1)
arrow(ax, 7.05, 4.6, 7.05, 3.65, "load (cached)", lx=0.6, ly=0.0)
arrow(ax, 8.3, 5.02, 9.0, 5.02, "load bundle")
arrow(ax, 10.15, 4.6, 10.15, 3.7, "write evidence", lx=0.65, ly=0.0)
arrow(ax, 9.0, 3.2, 8.3, 3.2, "case-study files", ly=0.1)
arrow(ax, 6.5, 2.75, 6.5, 1.35, "7-tab\ndashboard", lx=-0.5, ly=0.0)
arrow(ax, 7.6, 1.35, 7.6, 2.75, "patient choice,\nwhat-if edits,\nLIME seed", lx=0.6, ly=-0.1)
ax.text(0.2, 5.9, "Legend:  rounded = process (P)   square = data store (D)   blue = external entity",
        fontsize=8, color="#475467")
ax.set_title("ClinXAI level-1 data-flow diagram (files and scripts as implemented)", fontweight="bold", fontsize=11)
save(fig, "report_dfd.png")

# ------------------------------------------------------------------ explanation workflow (LIME vs SHAP lanes)
fig, ax = plt.subplots(figsize=(13, 4.6))
ax.set_xlim(0, 13); ax.set_ylim(0, 4.6); ax.axis("off")
L, S, C = "#FDF2E9", "#E6F4F1", "#FCE8EC"
box(ax, 0.1, 1.85, 1.7, 0.9, "Patient x\n(30 features,\ntraining order)", "#E8F1FA")
ax.text(2.1, 4.25, "LIME lane (explain_lime.py)", fontsize=9, fontweight="bold", color="#B54708")
for i, t in enumerate(["Quartile-discretise\nusing X_train stats", "Sample 5000\nperturbations z\n(seed 42)",
                       "RF predict_proba\nP(malignant | z)", "Weight by kernel\nπx(z)", "Weighted ridge\nsurrogate g → weights,\nintercept, R²"]):
    box(ax, 2.1 + i * 1.85, 3.1, 1.65, 0.95, t, L, fs=7.8)
    if i:
        arrow(ax, 2.1 + i * 1.85 - 0.2, 3.57, 2.1 + i * 1.85, 3.57)
ax.text(2.1, 1.35, "SHAP lane (explain_shap.py)", fontsize=9, fontweight="bold", color=ACCENT)
for i, t in enumerate(["TreeExplainer(model)\npath-dependent,\nno background", "shap_values(x)\nshape (1, 30, 2)",
                       "Select class 1\n(malignant) slice", "Check additivity\nφ0 + Σφi = P(mal)", "Local table,\nwaterfall, force"]):
    box(ax, 2.1 + i * 1.85, 0.2, 1.65, 0.95, t, S, fs=7.8)
    if i:
        arrow(ax, 2.1 + i * 1.85 - 0.2, 0.67, 2.1 + i * 1.85, 0.67)
arrow(ax, 1.8, 2.5, 2.1, 3.4)
arrow(ax, 1.8, 2.1, 2.1, 0.9)
box(ax, 11.45, 1.65, 1.45, 1.3, "comparison.py\ntop-5 Jaccard,\nSpearman ρ,\nsign agreement", C, fs=7.8)
arrow(ax, 11.25, 3.4, 11.9, 2.95)
arrow(ax, 11.25, 0.9, 11.9, 1.65)
ax.set_title("Per-patient explanation workflow: same patient, same Random Forest, same target class (malignant)",
             fontweight="bold", fontsize=11)
save(fig, "report_explanation_workflow.png")

# ------------------------------------------------------------------ Streamlit interaction flow
fig, ax = plt.subplots(figsize=(13, 4.4))
ax.set_xlim(0, 13); ax.set_ylim(0, 4.4); ax.axis("off")
box(ax, 0.1, 1.7, 2.0, 1.0, "Sidebar\npatient selectbox\nLIME seed · samples", "#E8F1FA")
box(ax, 2.6, 1.7, 2.0, 1.0, "Diagnostic tab\noptional what-if edits\n(8 top features)", "#E8F1FA")
box(ax, 5.1, 1.7, 2.1, 1.0, "validate_patient_input()\nfinite · non-negative\n· 30 named features", "#FDF2E9")
box(ax, 7.7, 2.9, 2.3, 0.9, "st.cache_resource\nmodel bundle, TreeExplainer,\ntest-set SHAP", "#F3F4F6")
box(ax, 7.7, 1.7, 2.3, 0.9, "st.cache_data\nLIME / SHAP keyed by\n(values, seed, samples)", "#F3F4F6")
box(ax, 7.7, 0.4, 2.3, 0.9, "Out-of-range check\n→ extrapolation warning", "#FDF2E9")
box(ax, 10.5, 0.4, 2.4, 3.4, "Tabs re-render\n\nOverview\nDiagnostic Prediction\nLIME Explanation\nSHAP Explanation\n"
    "LIME vs SHAP\nModel Evaluation\nCase Studies\n(\"Open patient\" button\n→ sidebar)", "#E6F4F1", fs=8)
arrow(ax, 2.1, 2.2, 2.6, 2.2)
arrow(ax, 4.6, 2.2, 5.1, 2.2)
arrow(ax, 7.2, 2.2, 7.7, 2.15)
arrow(ax, 7.2, 2.0, 7.7, 0.85)
arrow(ax, 10.0, 3.35, 10.5, 3.0)
arrow(ax, 10.0, 2.15, 10.5, 2.15)
arrow(ax, 10.0, 0.85, 10.5, 1.0)
ax.text(5.1, 2.95, "invalid → st.error + st.stop()", fontsize=7.5, color="#B42318", style="italic")
ax.set_title("Streamlit user-interaction flow (app.py): every widget change triggers a cached re-run",
             fontweight="bold", fontsize=11)
save(fig, "report_ui_flow.png")

# ------------------------------------------------------------------ confidence vs agreement (from saved CSV)
s = pd.read_csv(ROOT / "outputs" / "case_studies" / "test_set_lime_vs_shap.csv")
s["confidence"] = (s["p_malignant"] - 0.5).abs()
fn = (s["true_label"] == 1) & (s["predicted_label"] == 0)
fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
rng = np.random.default_rng(0)
jit = rng.uniform(-0.012, 0.012, len(s))  # display jitter only; values are unchanged in the CSV
for ax, col, lab in [(axes[0], "jaccard_top_k", "Top-5 Jaccard (LIME vs SHAP)"),
                     (axes[1], "lime_local_r2", "LIME local-surrogate R²")]:
    ax.scatter(s.loc[~fn, "confidence"], s.loc[~fn, col] + (jit[~fn] if col == "jaccard_top_k" else 0),
               s=18, color=ACCENT, alpha=0.7, label="Correct prediction")
    ax.scatter(s.loc[fn, "confidence"], s.loc[fn, col], s=60, marker="X", color=MALIGNANT_COLOR,
               label="False negative (#73, #86, #385)")
    for _, r in s[fn].iterrows():
        ax.annotate(f"#{int(r.patient_id)}", (r.confidence, r[col]), textcoords="offset points", xytext=(6, 4),
                    fontsize=8, color=MALIGNANT_COLOR)
    ax.set_xlabel("Model confidence |P(malignant) − 0.5|")
    ax.set_ylabel(lab)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
rho = s[["confidence", "jaccard_top_k", "lime_local_r2"]].corr(method="spearman")
axes[0].set_title(f"(a) Agreement vs confidence (Spearman ρ = {rho.loc['confidence', 'jaccard_top_k']:.2f})",
                  fontsize=10, fontweight="bold")
axes[1].set_title(f"(b) LIME fidelity vs confidence (Spearman ρ = {rho.loc['confidence', 'lime_local_r2']:.2f})",
                  fontsize=10, fontweight="bold")
fig.tight_layout()
save(fig, "report_confidence_vs_agreement.png")

hi, lo = s[s.confidence >= 0.4], s[s.confidence < 0.4]
stats = {
    "spearman_confidence_vs_jaccard": float(rho.loc["confidence", "jaccard_top_k"]),
    "spearman_confidence_vs_lime_r2": float(rho.loc["confidence", "lime_local_r2"]),
    "n_confident_ge_0.4": len(hi), "mean_jaccard_confident": float(hi.jaccard_top_k.mean()),
    "mean_r2_confident": float(hi.lime_local_r2.mean()),
    "n_uncertain_lt_0.4": len(lo), "mean_jaccard_uncertain": float(lo.jaccard_top_k.mean()),
    "mean_r2_uncertain": float(lo.lime_local_r2.mean()),
    "overlap_count_distribution": {int(k): int(v) for k, v in s.top_k_overlap.value_counts().sort_index().items()},
    "false_negatives": s.loc[fn, ["patient_id", "p_malignant", "jaccard_top_k", "spearman_abs_all_features",
                                  "lime_local_r2", "n_direction_disagreements"]].round(4).to_dict(orient="records"),
}
(OUT / "report_descriptive_analysis.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
print(json.dumps(stats, indent=1))
