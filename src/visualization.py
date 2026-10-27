"""Matplotlib figures for ClinXAI. Every function returns a Figure and never calls plt.show()."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import shap  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

# Shared palette: red = pushes toward malignant, blue = pushes toward benign (matches SHAP).
MALIGNANT_COLOR = "#C8102E"
BENIGN_COLOR = "#1E6FB8"
ACCENT = "#0B7A75"
INK = "#1F2A37"
GRID = "#E5E9F0"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.edgecolor": "#9AA5B1",
        "axes.labelcolor": INK,
        "axes.titleweight": "bold",
        "axes.titlesize": 12,
        "xtick.color": INK,
        "ytick.color": INK,
        "figure.dpi": 110,
        "savefig.bbox": "tight",
        "savefig.dpi": 150,
    }
)


def _style(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def save(fig, path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")


# ---------------------------------------------------------------- evaluation
def plot_confusion_matrix(cm: dict, title: str = "Confusion matrix (test set)"):
    mat = np.array([[cm["tn"], cm["fp"]], [cm["fn"], cm["tp"]]])
    fig, ax = plt.subplots(figsize=(4.6, 4))
    ax.imshow(mat, cmap="Blues")
    labels = [["True negative", "False positive"], ["False negative", "True positive"]]
    for i in range(2):
        for j in range(2):
            color = "white" if mat[i, j] > mat.max() / 2 else INK
            ax.text(j, i, f"{mat[i, j]}\n{labels[i][j]}", ha="center", va="center", color=color, fontsize=10)
    ax.set_xticks([0, 1], ["Benign (0)", "Malignant (1)"])
    ax.set_yticks([0, 1], ["Benign (0)", "Malignant (1)"])
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(title)
    fig.tight_layout()
    return fig


def plot_roc(curves: dict, title: str = "ROC curve — positive class: Malignant"):
    """curves: name -> (fpr, tpr, auc)."""
    fig, ax = plt.subplots(figsize=(5, 4.3))
    colors = [ACCENT, "#8E6C8A", "#D98E04"]
    for (name, (fpr, tpr, auc)), c in zip(curves.items(), colors):
        ax.plot(fpr, tpr, color=c, lw=2, label=f"{name} (AUC = {auc:.3f})")
    ax.plot([0, 1], [0, 1], ls="--", color="#9AA5B1", lw=1, label="Chance")
    ax.set_xlabel("False positive rate (1 − specificity)")
    ax.set_ylabel("True positive rate (sensitivity)")
    ax.set_title(title)
    ax.legend(loc="lower right", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def plot_risk_gauge(p: float, threshold: float = 0.5):
    """Horizontal probability bar with the decision threshold marked."""
    fig, ax = plt.subplots(figsize=(7, 1.35))
    grad = np.linspace(0, 1, 256).reshape(1, -1)
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("risk", [BENIGN_COLOR, "#F2F4F7", MALIGNANT_COLOR])
    ax.imshow(grad, extent=[0, 1, 0, 1], aspect="auto", cmap=cmap, alpha=0.85)
    ax.axvline(threshold, color=INK, ls="--", lw=1)
    ax.text(threshold, 1.08, f"threshold {threshold:.2f}", ha="center", va="bottom", fontsize=8, color=INK)
    ax.plot([p], [0.5], marker="v", markersize=16, color=INK, transform=ax.transData)
    ax.text(p, -0.12, f"P(malignant) = {p:.3f}", ha="center", va="top", fontsize=10, fontweight="bold", color=INK)
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, 1.4)
    ax.set_yticks([])
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.text(0.0, 1.08, "Benign", ha="left", va="bottom", fontsize=9, color=BENIGN_COLOR, fontweight="bold")
    ax.text(1.0, 1.08, "Malignant", ha="right", va="bottom", fontsize=9, color=MALIGNANT_COLOR, fontweight="bold")
    for s in ax.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------- LIME
def plot_lime(lime_table: pd.DataFrame, n: int = 10, title: str = "LIME local explanation — P(malignant)"):
    d = lime_table.head(n).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 0.42 * len(d) + 1.2))
    colors = [MALIGNANT_COLOR if w > 0 else BENIGN_COLOR for w in d["weight"]]
    ax.barh(d["rule"], d["weight"], color=colors)
    ax.axvline(0, color=INK, lw=0.8)
    ax.set_xlabel("Surrogate weight (+ toward malignant, − toward benign)")
    ax.set_title(title)
    _style(ax)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------- SHAP
def plot_shap_global_bar(importance: pd.Series, n: int = 15,
                         title: str = "Global feature importance — mean |SHAP| (test set)"):
    d = importance.head(n).iloc[::-1]
    fig, ax = plt.subplots(figsize=(7.5, 0.36 * len(d) + 1.2))
    ax.barh(d.index, d.values, color=ACCENT)
    ax.set_xlabel("mean |SHAP value| (change in P(malignant))")
    ax.set_title(title)
    _style(ax)
    fig.tight_layout()
    return fig


def plot_shap_beeswarm(explanation: shap.Explanation, max_display: int = 15):
    plt.close("all")
    try:
        shap.plots.beeswarm(explanation, max_display=max_display, show=False)
    except Exception:  # fallback for SHAP versions without the Explanation API
        shap.summary_plot(explanation.values, explanation.data, feature_names=explanation.feature_names,
                          max_display=max_display, show=False)
    fig = plt.gcf()
    fig.set_size_inches(8, 0.38 * max_display + 1.6)
    plt.title("SHAP summary (beeswarm) — impact on P(malignant)", fontweight="bold")
    fig.tight_layout()
    return fig


def plot_shap_waterfall(explanation_row: shap.Explanation, max_display: int = 12):
    plt.close("all")
    try:
        shap.plots.waterfall(explanation_row, max_display=max_display, show=False)
        fig = plt.gcf()
    except Exception:  # fallback: manual waterfall
        fig = _manual_waterfall(explanation_row, max_display)
    fig.set_size_inches(8.5, 0.42 * max_display + 1.8)
    fig.suptitle("SHAP waterfall — this patient (units: probability of malignant)", fontweight="bold", y=1.0)
    fig.tight_layout()
    return fig


def _manual_waterfall(row: shap.Explanation, max_display: int):
    vals = pd.Series(row.values, index=row.feature_names)
    order = vals.abs().sort_values(ascending=False).index[:max_display][::-1]
    fig, ax = plt.subplots()
    start = float(row.base_values)
    cum = start + vals.drop(order).sum()
    for i, f in enumerate(order):
        v = vals[f]
        ax.barh(i, v, left=cum, color=MALIGNANT_COLOR if v > 0 else BENIGN_COLOR)
        cum += v
    ax.set_yticks(range(len(order)), order)
    ax.axvline(start, color="#9AA5B1", ls="--")
    _style(ax)
    return fig


def plot_shap_force_matplotlib(explanation_row: shap.Explanation, top: int = 6):
    """Static force plot. The `top` strongest features are shown individually; the remainder are
    summed into 'other features (+/−)' groups, which keeps base + sum(SHAP) = f(x) exact."""
    plt.close("all")
    vals = np.asarray(explanation_row.values, dtype=float)
    data = np.asarray(explanation_row.data, dtype=float)
    names = list(explanation_row.feature_names)
    keep = list(np.argsort(-np.abs(vals))[:top])
    rest = [i for i in range(len(vals)) if i not in keep]
    pos_rest = [i for i in rest if vals[i] > 0]
    neg_rest = [i for i in rest if vals[i] <= 0]

    f_vals = [vals[i] for i in keep]
    f_data = [f"{data[i]:.4g}" if abs(data[i]) < 1000 else f"{data[i]:.0f}" for i in keep]
    f_names = [names[i] for i in keep]
    for group, sign in ((pos_rest, "+"), (neg_rest, "−")):
        if group:
            f_vals.append(vals[group].sum())
            f_data.append("")
            f_names.append(f"{len(group)} other features ({sign})")
    try:
        shap.plots.force(float(explanation_row.base_values), np.array(f_vals), np.array(f_data, dtype=object),
                         feature_names=f_names, matplotlib=True, show=False, text_rotation=12,
                         contribution_threshold=0.03)
        fig = plt.gcf()
        fig.set_size_inches(14, 3.6)
    except Exception:
        fig = _manual_waterfall(explanation_row, top)
    return fig


def shap_force_html(explanation_row: shap.Explanation) -> str:
    """Interactive force plot as a standalone HTML string (bundles SHAP's JS)."""
    plot = shap.plots.force(
        float(explanation_row.base_values),
        np.asarray(explanation_row.values, dtype=float),
        np.round(np.asarray(explanation_row.data, dtype=float), 3),
        feature_names=list(explanation_row.feature_names),
        out_names="P(malignant)",
    )
    return f"<html><head><meta charset='utf-8'>{shap.getjs()}</head><body>{plot.html()}</body></html>"


# ---------------------------------------------------------------- LIME vs SHAP
def plot_lime_vs_shap(direction_table: pd.DataFrame, title: str = "LIME vs SHAP — same patient, same class"):
    """Side-by-side bars over the union of both top-k lists. Independent x-axes because the
    two methods' magnitudes have different meanings."""
    d = direction_table.sort_values("shap_rank", ascending=False)
    fig, axes = plt.subplots(1, 2, figsize=(11, 0.45 * len(d) + 1.6), sharey=True)
    for ax, col, name in [(axes[0], "lime_weight", "LIME surrogate weight"),
                          (axes[1], "shap_value", "SHAP value (Δ probability)")]:
        colors = [MALIGNANT_COLOR if v > 0 else BENIGN_COLOR for v in d[col]]
        ax.barh(d["feature"], d[col], color=colors)
        ax.axvline(0, color=INK, lw=0.8)
        ax.set_xlabel(name)
        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(5))
        _style(ax)
    for i, (_, r) in enumerate(d.iterrows()):
        if not r["same_direction"]:
            axes[1].text(1.01, i, "⚠ direction differs", transform=axes[1].get_yaxis_transform(),
                         va="center", fontsize=8, color="#B54708")
    axes[0].set_title("LIME (rank by |weight|)")
    axes[1].set_title("SHAP (rank by |value|)")
    fig.suptitle(title, fontweight="bold")
    fig.tight_layout()
    return fig


def plot_case_study_overview(cases: pd.DataFrame):
    """Top-5 Jaccard and Spearman per case study."""
    d = cases[cases["found"]].copy()
    labels = [f"{t}\n(patient {int(p)})" for t, p in zip(d["case_type"], d["patient_id"])]
    x = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(9, 4))
    for offset, col, color, label in [(-0.2, "jaccard_top_k", ACCENT, "Top-5 Jaccard"),
                                      (0.2, "spearman_abs_all_features", "#8E6C8A", "Spearman ρ (|attr|, 30 features)")]:
        bars = ax.bar(x + offset, d[col], 0.4, color=color, label=label)
        ax.bar_label(bars, fmt="%.2f", fontsize=8, padding=2)
    ax.set_xticks(x, labels, fontsize=8)
    ax.set_ylim(min(0, d["spearman_abs_all_features"].min() - 0.1), 1.05)
    ax.axhline(0, color=INK, lw=0.6)
    ax.set_ylabel("Agreement")
    ax.set_title("LIME–SHAP agreement across case studies")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------- architecture
def plot_architecture():
    fig, ax = plt.subplots(figsize=(12, 4.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4.2)
    ax.axis("off")

    def box(x, y, w, h, text, fc):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.15",
                                    fc=fc, ec=INK, lw=1))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9, color=INK, wrap=True)

    def arrow(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", color=INK, lw=1.3))

    box(0.2, 1.6, 1.9, 1.0, "Breast Cancer\nWisconsin (569×30)\nmalignant = 1", "#E8F1FA")
    box(2.6, 1.6, 1.9, 1.0, "Stratified 80/20\nsplit (seed 42)", "#E8F1FA")
    box(5.0, 1.6, 1.9, 1.0, "Random Forest\n(300 trees)\n+ LR baseline", "#E6F4F1")
    box(7.5, 3.0, 2.0, 0.95, "LIME\nlocal surrogate\n(train-data stats)", "#FDF2E9")
    box(7.5, 1.6, 2.0, 0.95, "SHAP TreeExplainer\nlocal + global\n(additivity check)", "#FDF2E9")
    box(7.5, 0.2, 2.0, 0.95, "Evaluation\nAcc/Prec/Rec/F1/AUC\nconfusion, ROC", "#F3F4F6")
    box(10.0, 1.6, 1.8, 1.0, "LIME vs SHAP\ncomparison +\ncase studies", "#FCE8EC")
    box(10.0, 3.0, 1.8, 0.95, "Streamlit\ndashboard", "#E6F4F1")
    arrow(2.1, 2.1, 2.6, 2.1)
    arrow(4.5, 2.1, 5.0, 2.1)
    arrow(6.9, 2.3, 7.5, 3.4)
    arrow(6.9, 2.1, 7.5, 2.1)
    arrow(6.9, 1.9, 7.5, 0.7)
    arrow(9.5, 3.45, 10.0, 2.4)
    arrow(9.5, 2.1, 10.0, 2.1)
    arrow(10.9, 2.6, 10.9, 3.0)
    ax.set_title("ClinXAI architecture — tabular clinical diagnostics with two complementary explainers",
                 fontweight="bold")
    return fig
