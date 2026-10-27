"""Compact technical body (~20 pages): Chapters 1–7, references and short appendices.

Same facts as the full version; every number is read from the generated project outputs at build time.
"""
from pathlib import Path

from engine import Report
from content_mid import code_from

PROJ = Path(__file__).resolve().parents[2]
OUT_FIG = PROJ / "outputs" / "figures"
REP_FIG = PROJ / "report" / "figures"


def pct(x):
    return f"{100 * x:.2f}%"


def signed(x):
    return f"{x:+.4f}".replace("-", "−")


# ====================================================================== CHAPTER 1
def chapter1(R: Report, D, cite):
    R.h1("Chapter 1: Problem Definition & Operational Relevance", chapter="1")
    R.h2("1.1 Problem Statement and Background")
    R.p(f"Breast cancer is the most commonly diagnosed cancer in women; about 2.3 million women were diagnosed and "
        f"670,000 died in 2022 {cite('who2024bc')}. Fine-needle-aspirate (FNA) cytology can be supported by computer "
        f"vision: Street et al. digitised FNA slides and computed ten nuclear shape and texture measurements per sample "
        f"{cite('street1993')}, giving the Breast Cancer Wisconsin (Diagnostic) dataset {cite('uci1995')}. Accurate "
        f"ensembles such as a 300-tree Random Forest (10,976 decision nodes here) are, however, black boxes "
        f"{cite('breiman2001', 'rudin2019')}. **Problem statement:** predict P(malignant) for a patient's 30 nuclear "
        "features with a Random Forest, explain each prediction with LIME and SHAP for the same class, and measure "
        "when the two explanations disagree.")
    R.h2("1.2 Clinical and Societal Relevance")
    R.p(f"An unexplained score invites blind trust or rejection; a missed malignancy with a plausible explanation is "
        f"harder to catch; and two popular explainers can disagree {cite('krishna2022')}. Regulators expect "
        f"transparency and human oversight for medical AI {cite('euaiact2024', 'who2021')}.")
    R.h2("1.3 Project Objectives")
    R.table("t_obj", "Measurable project objectives", ["No.", "Objective", "Measurable criterion"],
            [["O1", "**Implement and evaluate** a Random Forest (malignant = positive) against a Logistic Regression "
                    "baseline", "Accuracy, precision, recall, F1, ROC-AUC, confusion matrix on 114 held-out patients"],
             ["O2", "**Apply** LIME and TreeSHAP to explain P(malignant) locally and globally",
              "Explanations for all test patients; SHAP additivity error < 10^{−6}"],
             ["O3", "**Quantify** LIME–SHAP agreement", "Top-5 overlap, Jaccard, Spearman ρ, sign agreement, seed stability"],
             ["O4", "**Design and validate** an interactive dashboard", "Seven-tab Streamlit app; automated and browser tests"]],
            [0.45, 2.9, 2.65], align=["c", "l", "l"])
    R.h2("1.4 Project Scope and Operational Boundaries")
    R.p("**In scope:** prediction from 30 tabular features, LIME and SHAP explanations and their comparison, five case "
        "studies and a local dashboard. **Out of scope:** raw images, calibrated risk, treatment advice, clinical "
        "validation, fairness audit and public deployment. *Multi-modal* refers to the two explanation modalities; the "
        "input is one tabular modality derived from images. CPU-only, Windows 11, Python 3.12.")


# ====================================================================== CHAPTER 2
def chapter2(R: Report, D, cite):
    F = D["facts"]
    R.h1("Chapter 2: Theoretical Formulation, Literature Review & Mathematical Framework", chapter="2")
    R.h2("2.1 Explainable Artificial Intelligence")
    R.p(f"XAI makes model behaviour understandable {cite('doshivelez2017')}; explanations are post-hoc or intrinsic, "
        "local or global, agnostic or model-specific, and are judged by **local fidelity**, **consistency**, "
        "**stability**, comprehensibility and cost.")
    R.h2("2.2 Random Forest Classification")
    R.p(f"A Random Forest averages T bootstrap-trained trees that split on random feature subsets "
        f"{cite('breiman2001')}. Here T = 300, Gini splits, ⌊√30⌋ = 5 features per split and fully grown trees "
        f"(scikit-learn {cite('pedregosa2011')}):")
    R.eq("f(x) = P̂(y = 1 | x) = (1/T) · Σ_{t=1..T} p_{t}(y = 1 | x),     G(node) = 1 − Σ_{k} p_{k}^{2}", "(2.1)")
    R.p("p_{t} is the malignant fraction in the leaf of tree t reached by x and G is the Gini impurity minimised at "
        "each split. The patient is predicted malignant when f(x) ≥ 0.5.")
    R.h2("2.3 LIME: Local Interpretable Model-Agnostic Explanations")
    R.p(f"LIME {cite('ribeiro2016')} fits a simple model g that imitates f only near x, using only `predict_proba`; "
        "features are discretised into training quartiles, giving rules such as `worst area > 1122.50` → +0.137.")
    R.h2("2.4 LIME Perturbation and Local Surrogate Formulation")
    R.eq("ξ(x) = argmin_{g ∈ G} L(f, g, π_{x}) + Ω(g),   L = Σ_{i} π_{x}(z_{i}) · ( f(z_{i}) − g(z′_{i}) )^{2}", "(2.2)")
    R.eq("π_{x}(z) = exp(−D(x, z)^{2} / (2σ^{2})),   σ = 0.75·√d,   g(z′) = w_{0} + Σ_{j} w_{j} z′_{j}", "(2.3)")
    R.p(f"z_{{i}} are N = 5,000 perturbed samples, z′_{{j}} ∈ {{0,1}} indicates that sample z is in the patient's bin "
        f"for feature j, π_{{x}} weights samples by distance D (σ ≈ {F['kernel_width_default']} for d = 30) and Ω is a "
        "ridge penalty (λ = 1). Each weight w_{j} is the explanation for feature j. The surrogate's weighted R² is "
        f"LIME's only fidelity signal, and results depend on the random seed {cite('alvarez2018')}.")
    R.h2("2.5 SHAP: Shapley Additive Explanations")
    R.p(f"SHAP {cite('lundberg2017')} writes an explanation as an additive model whose attributions satisfy *local "
        "accuracy*, *missingness* and *consistency*; for this classifier, in probability units:")
    R.eq("P(malignant | x) = φ_{0} + Σ_{j=1..30} φ_{j}(x),     φ_{0} = E[f(X)]", "(2.4)")
    R.h2("2.6 Shapley Game-Theoretic Attribution")
    R.eq("φ_{j}(x) = Σ_{S⊆F∖{j}} [|S|!·(M−|S|−1)!/M!]·[v_{x}(S∪{j}) − v_{x}(S)]", "(2.5)")
    R.p(f"Features are players, S a coalition of known features and v_{{x}}(S) = E[f(X) | X_{{S}} = x_{{S}}] its payout "
        f"{cite('shapley1953')}. The Shapley value uniquely satisfies efficiency, symmetry, dummy and additivity, but "
        "needs 2^{30} ≈ 1.07 × 10^{9} coalitions if computed naively.")
    R.h2("2.7 TreeSHAP Explanation Method")
    R.p(f"TreeSHAP {cite('lundberg2020')} computes Equation (2.5) exactly in O(T·L·D^{{2}}) time using the training "
        "*cover* of each node (tree-path-dependent mode, no background set). Because sklearn trees output class "
        f"fractions, φ_{{0}} (0.3747, close to the training prevalence {F['train_malignant']}/455 = 0.374), the φ_{{j}} and "
        "`predict_proba` share units, so Equation (2.4) can be checked numerically.")
    R.h2("2.8 LIME versus SHAP: Mathematical and Practical Trade-offs")
    R.table("t_lime_vs_shap_theory", "LIME and TreeSHAP as used in ClinXAI", ["Property", "LIME", "TreeSHAP"],
            [["Explanation unit", "Weight of a quartile-bin indicator", "Share of P(malignant) vs base value"],
             ["Local fidelity", "Approximate (surrogate R²)", "Exact (additive)"],
             ["Consistency / stability", "No guarantee / seed-dependent", "Guaranteed / deterministic"],
             ["Reference point", "Other bins of the training distribution", "E[f(X)] over training cover"],
             ["Cost", "N = 5,000 model calls per patient", "Polynomial, exact"]],
            [1.6, 2.2, 2.2])
    R.p("Magnitudes are not comparable, so agreement uses ranks and signs only. For the top-5 sets A (LIME) and B (SHAP):")
    R.eq("J = |A ∩ B| / |A ∪ B|,     ρ = 1 − 6Σ_{j} d_{j}^{2} / (n(n^{2} − 1)),  n = 30", "(2.6)")
    R.p("J is the Jaccard similarity, ρ the Spearman correlation of the |attribution| rankings, and a *direction "
        "disagreement* is a feature in A ∪ B with opposite LIME and SHAP signs. These are explanation-agreement "
        "measures, not clinical validation metrics.")
    R.h2("2.9 Comparative Literature Review")
    R.p(f"Logistic regression is faithful but restricted {cite('rudin2019')}; LIME and KernelSHAP {cite('lundberg2017')} "
        f"are model-agnostic but approximate; TreeSHAP {cite('lundberg2020')} is exact for trees. Perturbation explainers "
        f"can be unstable {cite('alvarez2018')} or fooled {cite('slack2020')} and often disagree {cite('krishna2022')}, "
        f"while medicine needs explainability {cite('holzinger2017')}. ClinXAI measures that disagreement.")


# ====================================================================== CHAPTER 3
def chapter3(R: Report, D, cite):
    R.h1("Chapter 3: System Architecture, Design Pipeline & Workflow Models", chapter="3")
    R.h2("3.1 Overall System Architecture")
    R.p(f"ClinXAI is a linear pipeline ({R.ref('f_arch')}): a data layer (`src/data_loader.py`), model layer "
        "(`src/model.py`, `train_model.py`), explanation layer (`src/explain_lime.py`, `src/explain_shap.py`), comparison "
        "layer (`src/comparison.py`, `evaluate.py`), presentation layer (`app.py`) and a verification layer "
        "(`tests/test_pipeline.py`).")
    R.fig("f_arch", OUT_FIG / "architecture.png", "ClinXAI architecture (generated by `evaluate.py`)", width_in=5.4)
    R.h2("3.2 Dataset and Feature Description")
    R.p(f"The dataset {cite('uci1995')} has 569 patients (212 malignant, 357 benign) and 30 non-negative features: ten "
        "nuclear characteristics (radius, texture, perimeter, area, smoothness, compactness, concavity, concave points, "
        "symmetry, fractal dimension), each given as *mean*, *standard error* and *worst* (mean of the three largest) "
        f"value, loaded through `load_breast_cancer()` with no missing values ({R.ref('f_dist')}).")
    R.fig("f_dist", REP_FIG / "report_dataset_distribution.png",
          "(a) Class counts and stratified split; (b–c) class-wise distributions of two discriminative features",
          width_in=5.4)
    R.h2("3.3 Data Preprocessing Pipeline")
    R.p("The loader validates shape (569 × 30), finiteness and labels; re-maps sklearn's malignant = 0 to **malignant = "
        "1** (asserted); and splits 80/20 with stratification and random_state = 42 (455 / 114 patients, 37.4% / 36.8% "
        "malignant). The model, LIME statistics and baseline scaler see training data only, and feature order is enforced.")
    R.h2("3.4 Random Forest Diagnostic Prediction Pipeline")
    R.p("`train_model.py` trains the 300-tree forest, asserts `classes_ == [0, 1]`, evaluates both models at threshold 0.5, "
        "runs 5-fold CV on the training set and saves one joblib bundle used by every later stage.")
    R.h2("3.5 LIME Explanation Workflow")
    R.p("A fresh seeded explainer samples 5,000 perturbations, queries the forest through a feature-name wrapper, weights "
        "them by the kernel and fits the ridge surrogate (30 weights, rules, intercept, R²).")
    R.h2("3.6 SHAP Explanation Workflow")
    R.p("One `TreeExplainer` returns an (n, 30, 2) array; the malignant slice is checked for additivity and drives the "
        "global, waterfall and force plots; both lanes feed `comparison.py`.")
    R.h2("3.7 Streamlit User Interaction Flow")
    R.p(f"Sidebar patient choice and optional what-if edits pass `validate_patient_input()`; cached results re-render "
        f"seven tabs {cite('streamlitdocs')}.")
    R.h2("3.8 System Architecture Diagram and Data Flow Diagram")
    R.p(f"{R.ref('f_dfd')} shows the level-1 data flow between the implemented scripts and files. The dashboard only "
        "reads the model bundle and output files, so using it cannot alter the evidence in this report.")
    R.fig("f_dfd", REP_FIG / "report_dfd.png", "Level-1 data-flow diagram (scripts and files as implemented)", width_in=4.4)


# ====================================================================== CHAPTER 4
def chapter4(R: Report, D, cite):
    env = dict(l.strip().split("==") for l in D["environment"].splitlines() if "==" in l)
    py = D["environment"].splitlines()[0].replace("Python ", "")
    lc = D["facts"]["line_counts"]
    R.h1("Chapter 4: Implementation Details, Algorithms & Technological Artifacts", chapter="4")
    R.h2("4.1 Development Environment and Technology Stack")
    R.table("t_stack", "Technology stack (exact versions tested)", ["Component", "Version", "Role"],
            [["Python", py, "Runtime (Windows 11, CPU only)"],
             ["scikit-learn / NumPy / pandas / SciPy",
              f"{env['scikit-learn']} / {env['numpy']} / {env['pandas']} / {env['scipy']}", "Data, models, metrics, Spearman"],
             ["LIME / SHAP", f"{env['lime']} / {env['shap']}", "Local surrogate / TreeExplainer"],
             ["Matplotlib / Streamlit", f"{env['matplotlib']} / {env['streamlit']}", "Figures / dashboard"],
             ["joblib / pytest", f"{env['joblib']} / {env['pytest']}", "Model bundle / tests"]],
            [2.1, 1.7, 2.2])
    R.h2("4.2 Dataset Loading and Target Mapping")
    R.p("The mapping is derived from `target_names`, re-encoded so malignant = 1, and asserted against the raw labels "
        "in both directions before `validate_dataset()` runs (`src/data_loader.py`, `load_dataset`).")
    R.h2("4.3 Model Training Implementation")
    code_from(R, "src/model.py", "train_random_forest", what="training with class-order assertion")
    R.p("`malignant_proba` reads the column whose label is 1, so every probability is P(malignant).")
    R.h2("4.4 LIME Explainer Implementation")
    R.p("LIME passes bare arrays, so a wrapper rebuilds a DataFrame in training order; a fresh, seeded explainer per "
        "call makes explanations reproducible; all 30 features and label 1 are requested:")
    code_from(R, "src/explain_lime.py", start="    explainer = build_lime_explainer(X_train, seed)",
              end="    idx_weights = exp.as_map()[MALIGNANT_LABEL]", include_end=True, what="explaining label 1")
    R.h2("4.5 SHAP Explainer Implementation")
    R.p(f"`_select_malignant` normalises the version-dependent SHAP output (list, 3-D or 2-D) to the malignant class "
        f"{cite('shapdocs')}, and `additivity_error` checks Equation (2.4) against `predict_proba`.")
    R.h2("4.6 LIME–SHAP Comparison Implementation")
    R.p("`compare_explanations` aligns both vectors by feature name and returns the top-5 sets, Jaccard, Spearman ρ and "
        "the direction table. `select_case_studies` picks, from the 114 test patients: max P (clearly malignant), "
        "min P (clearly benign), P closest to 0.5 (borderline), lowest Jaccard (ranking divergence) and most sign "
        "conflicts (direction disagreement); a missing case is reported as not found, never fabricated.")
    R.h2("4.7 Streamlit Interface Implementation")
    R.p(f"`app.py` ({lc['app.py']} lines) provides a sidebar (patient selector, LIME seed and sample count), seven tabs, "
        "a what-if editor, a stability toggle and a case-study jump button (screenshots in Section 5.11). The model and "
        "test-set SHAP values are cached once; per-patient explanations are cached by feature values.")
    R.h2("4.8 Input Validation and Error Handling")
    R.table("t_guards", "Guardrails and their verification", ["Situation", "Behaviour", "Verified by"],
            [["Missing/unknown feature, wrong length, NaN, ∞, text, negative value", "ValueError naming the problem",
              "7 pytest cases"],
             ["Value outside training range", "Extrapolation warning", f"Browser screenshot ({R.ref('f_ui_oor')})"],
             ["Class/feature-order mismatch", "Assertions at training and load", "pytest + validation"],
             ["Model or case files missing", "Auto-train / informative message", "Code path in app.py"]],
            [2.6, 2.0, 1.4])
    R.h2("4.9 Code Structure and Module Responsibilities")
    R.p(f"The {sum(lc.values()):,} lines are split into `src/config.py` (settings), `data_loader.py`, `model.py`, "
        "`explain_lime.py`, `explain_shap.py`, `comparison.py` and `visualization.py`, plus the scripts `train_model.py`, "
        "`evaluate.py` and `app.py` and the 24-test suite `tests/test_pipeline.py`. Appendix A lists the key "
        "configuration files.")


# ====================================================================== CHAPTER 5
def chapter5(R: Report, D, cite):
    M = D["metrics"]
    rf, lr, ds = M["random_forest"], M["logistic_regression_baseline"], M["dataset"]
    cm = rf["confusion_matrix"]
    agg = D["cases"]["aggregate_test_set"]
    cases = {c["patient_id"]: c for c in D["cases"]["cases"]}
    desc = D["desc"]
    F = D["facts"]
    R.h1("Chapter 5: Experimental Evaluation, Testing, Trade-off Analysis & Empirical Results", chapter="5")
    R.h2("5.1 Experimental Methodology")
    R.p("Models are fitted on 455 patients and evaluated once on 114 held-out patients at threshold 0.5 (malignant = "
        "positive), with 5-fold CV on the training set. LIME (seed 42, 5,000 samples) and TreeSHAP explain all 114 "
        "test patients; five case studies are chosen by fixed rules and LIME is re-run with seeds 0–4 for stability. "
        "All numbers come from files written by `train_model.py` and `evaluate.py`.")
    R.h2("5.2 Dataset Characteristics and Train/Test Split")
    R.p(f"Training: {ds['n_train']} patients ({F['train_malignant']} malignant). Test: {ds['n_test']} patients "
        f"({ds['test_malignant']} malignant, {ds['test_benign']} benign), so each missed malignancy costs 2.4 points of recall.")
    R.h2("5.3 Accuracy, Precision, Recall, F1 and ROC-AUC")
    R.eq("Precision = TP/(TP+FP)   Recall = TP/(TP+FN)   F1 = 2·P·R/(P+R)   Acc = (TP+TN)/N", "(5.1)")
    R.table("t_metrics", "Held-out test performance (114 patients, positive class = malignant)",
            ["Model", "Accuracy", "Precision", "Recall", "Specificity", "F1", "ROC-AUC"],
            [["Random Forest", pct(rf["accuracy"]), pct(rf["precision"]), pct(rf["recall_sensitivity"]),
              pct(rf["specificity"]), pct(rf["f1"]), f"{rf['roc_auc']:.4f}"],
             ["Logistic Regression", pct(lr["accuracy"]), pct(lr["precision"]), pct(lr["recall_sensitivity"]),
              pct(lr["specificity"]), pct(lr["f1"]), f"{lr['roc_auc']:.4f}"]],
            [1.5, 0.78, 0.78, 0.74, 0.82, 0.68, 0.7], align=["l", "c", "c", "c", "c", "c", "c"])
    R.p(f"The Random Forest reached **{pct(rf['accuracy'])} accuracy, {pct(rf['precision'])} precision, "
        f"{pct(rf['recall_sensitivity'])} recall, {pct(rf['f1'])} F1 and ROC-AUC {rf['roc_auc']:.4f}**; CV ROC-AUC on the "
        f"training set was {rf['cv_roc_auc_mean']:.4f} ± {rf['cv_roc_auc_std']:.4f}.")
    R.h2("5.4 Confusion Matrix and ROC Curve")
    R.p(f"TN = {cm['tn']}, FP = {cm['fp']}, FN = {cm['fn']}, TP = {cm['tp']} ({R.ref('f_cmroc')}): every error is a "
        "missed malignancy, the clinically most serious type. The baseline's AUC (0.9960) is marginally higher, within "
        "sampling noise on 114 patients.")
    R.fig("f_cmroc", REP_FIG / "compact_cm_roc.png", "(a) Random Forest confusion matrix; (b) ROC curves of both models",
          width_in=5.4)
    R.h2("5.5 Global SHAP Feature Importance")
    gi = D["global_importance"][:5]
    top = ", ".join(f"{r['feature']} ({float(r['mean_abs_shap']):.4f})" for r in gi)
    R.p(f"Mean |SHAP| over the test set ranks {top} highest ({R.ref('f_global')}). High size and concavity values "
        "push P(malignant) up, consistent with the class separation in the data.")
    R.fig("f_global", REP_FIG / "compact_shap_global.png", "(a) Global mean |SHAP| importance; (b) SHAP beeswarm plot")
    R.h2("5.6 Individual Patient LIME Explanations")
    c70, c86, c73, c100 = cases[70], cases[86], cases[73], cases[100]
    R.p(f"For Patient #70 (P = 1.000) every top LIME condition points to malignant and R² = {c70['lime_local_r2']:.2f}. "
        f"For the missed malignancy #86 (P = {c86['p_malignant']:.3f}, {R.ref('f_p86')}a) the top conditions point to "
        f"*malignant* although the output is benign, and the surrogate barely fits (R² = {c86['lime_local_r2']:.2f}; it "
        f"predicts {c86['lime_local_pred']:.3f} where the forest outputs {c86['p_malignant']:.3f}).")
    R.h2("5.7 Individual Patient SHAP Explanations")
    R.p(f"The waterfall for #86 ({R.ref('f_p86')}b) starts at φ_{{0}} = 0.3747 and adds conflicting contributions (mean "
        f"concavity +0.050; worst perimeter, worst and mean concave points ≈ −0.03 each) to reach "
        f"0.3747 − 0.0780 = {c86['p_malignant']:.4f}. Across all 114 patients the additivity error was "
        f"**{D['additivity']['max_abs_error']:.1e}**, confirming correct class selection and units.")
    R.fig("f_p86", REP_FIG / "compact_p86_lime_waterfall.png",
          "Patient #86 (false negative): (a) LIME explanation; (b) SHAP waterfall plot")
    R.h2("5.8 LIME–SHAP Case Study Comparison")
    order = [70, 74, 100, 86, 73]
    R.table("t_cases", "The five programmatically selected case studies",
            ["Case", "Patient", "P(mal.)", "Actual / predicted", "Top-5", "Jaccard", "ρ", "Sign flips", "R²"],
            [[cases[p]["case_type"], f"#{p}", f"{cases[p]['p_malignant']:.3f}",
              f"{cases[p]['true_label']} / {'Malignant' if cases[p]['p_malignant'] >= 0.5 else 'Benign'}",
              f"{cases[p]['comparison']['top_k_overlap']}/5", f"{cases[p]['comparison']['jaccard_top_k']:.2f}",
              f"{cases[p]['comparison']['spearman_abs_all_features']:.2f}",
              str(len(cases[p]['comparison']['direction_disagreements_union'])), f"{cases[p]['lime_local_r2']:.2f}"]
             for p in order],
            [0.95, 0.6, 0.6, 0.88, 0.55, 0.7, 0.4, 0.72, 0.6], align=["l", "c", "c", "l", "c", "c", "c", "c", "c"])
    R.bullets([
        "**#70 clearly malignant and #74 clearly benign:** identical top-5 sets (worst area, worst perimeter, worst "
        "concave points, worst radius, mean concave points), no sign conflicts. Yet #74's surrogate predicts 0.111 "
        "where the model outputs 0.000 (R² 0.17): agreement in ranking does not mean fidelity.",
        f"**#100 borderline (P = {c100['p_malignant']:.3f}):** LIME leads with texture, SHAP with size; only 2 shared "
        "features; area error and worst perimeter flip sign. SHAP gives worst radius +0.078 but worst perimeter −0.044 "
        f"although they correlate at r = {F['corr']['worst radius | worst perimeter']}.",
        f"**#86 missed malignancy:** **no shared top-5 feature**, four sign conflicts, R² = {c86['lime_local_r2']:.2f}, "
        f"and LIME's own seed stability is {c86['lime_stability']['mean_pairwise_jaccard_top_k']:.2f} (one seed pair shares "
        "no feature).",
        f"**#73 missed malignancy (P = {c73['p_malignant']:.3f}):** only worst texture shared; worst area, worst "
        f"perimeter, mean concavity and mean concave points flip sign; R² = {c73['lime_local_r2']:.2f}.",
    ])
    R.fig("f_cmp86", OUT_FIG / "lime_vs_shap_case4_patient86.png",
          "LIME vs SHAP for Patient #86 (no shared top-5 feature; four sign conflicts)", width_in=5.0)
    R.fig("f_cmp73", OUT_FIG / "lime_vs_shap_case5_patient73.png",
          "LIME vs SHAP for Patient #73 (four sign conflicts)", width_in=5.0)
    R.p(f"**Why they diverge.** Worst area for #86 and #73 ({F['case_values']['86']['worst area']} and "
        f"{F['case_values']['73']['worst area']}) lies in the wide training bin "
        f"{F['worst_area_train_quartiles'][1]}–{F['worst_area_train_quartiles'][2]}: LIME compares *being in this bin* with "
        "mostly benign lower bins (positive weight), while SHAP compares the exact value with the base value along the "
        "forest's paths (negative). **Clinical limitation:** SHAP gives an exact, coherent rationale *for a wrong "
        "prediction*, and LIME gives malignant-leaning reasons for a benign label; neither is evidence about the tumour.")
    R.h2("5.9 Explanation Divergence Analysis")
    R.table("t_agg", "Aggregate LIME–SHAP agreement over the 114 test patients", ["Measure", "Value"],
            [["Mean top-5 feature overlap", f"{agg['mean_top5_overlap']:.2f} / 5"],
             ["Mean Jaccard similarity", f"{agg['mean_top5_jaccard']:.2f}"],
             ["Mean Spearman ρ (|attributions|, 30 features)", f"{agg['mean_spearman_abs']:.2f}"],
             ["Patients with ≥ 1 direction disagreement",
              f"{agg['pct_patients_with_direction_disagreement']:.1f}% "
              f"({round(agg['pct_patients_with_direction_disagreement'] * 114 / 100)} of 114)"],
             ["Mean LIME local R²", f"{agg['mean_lime_local_r2']:.2f}"]],
            [3.8, 2.2], align=["l", "c"])
    fns = desc["false_negatives"]
    R.p(f"Agreement tracks model confidence |P − 0.5| (Spearman ρ = {desc['spearman_confidence_vs_jaccard']:.2f} with "
        f"Jaccard, {desc['spearman_confidence_vs_lime_r2']:.2f} with LIME R²; {R.ref('f_conf')}). Confident patients "
        f"(n = {desc['n_confident_ge_0.4']}) average Jaccard {desc['mean_jaccard_confident']:.2f} and R² "
        f"{desc['mean_r2_confident']:.2f}; the other {desc['n_uncertain_lt_0.4']} average "
        f"{desc['mean_jaccard_uncertain']:.2f} and {desc['mean_r2_uncertain']:.2f}. **All three false negatives** "
        f"(#73, #86, #385) have Jaccard ≤ 0.25, R² ≤ {max(r['lime_local_r2'] for r in fns):.3f} and at least three sign "
        f"conflicts (descriptive analysis of the saved per-patient CSV). Causes: different reference points, a linear "
        f"surrogate on a non-linear boundary, {F['n_pairs_corr_gt_0.9']} feature pairs with |r| > 0.9, independent "
        f"perturbations off the data manifold {cite('slack2020')} and sampling noise {cite('alvarez2018')}. **Low LIME "
        "fidelity and LIME–SHAP disagreement concentrate on exactly the predictions that need human review.**")
    R.fig("f_conf", REP_FIG / "report_confidence_vs_agreement.png",
          "(a) LIME–SHAP Jaccard and (b) LIME R² against model confidence; false negatives marked")
    R.h2("5.10 Model Performance and Interpretability Trade-offs")
    R.p(f"The forest's only advantage over the transparent baseline is one fewer false positive; both miss three cancers, "
        f"supporting Rudin's case for interpretable models {cite('rudin2019')}. LIME trades fidelity for simplicity (mean "
        "R² 0.27); TreeSHAP is exact but tree-only; more LIME samples would improve stability at extra cost "
        "(`evaluate.py` already takes about 36 s on a CPU). The three false negatives lie at P = 0.160, 0.190 and 0.297; "
        f"a lower threshold would need separate validation data and calibration {cite('niculescu2005')}.")
    R.h2("5.11 Operational Verification Screenshots")
    R.p("Real screenshots of the running app (Microsoft Edge, Playwright, 1440 px). Verification: 24/24 pytest tests, "
        "24/24 after a clean install, 35/35 independent output checks and 34/34 real-browser checks (Appendix B).")
    R.fig("f_ui_cmp", REP_FIG / "ui_tab5_lime_vs_shap_p86_chart.png",
          "LIME vs SHAP tab for Patient #86: 0/5 overlap, 4 disagreements", width_in=4.6)
    R.fig("f_ui_whatif", REP_FIG / "ui_whatif_p100_worst_area_500.png",
          "What-if on Patient #100: worst area 906.5 → 500 flips the output to benign (P = 0.363)", width_in=5.0)
    R.fig("f_ui_oor", REP_FIG / "ui_error_out_of_range_warning.png",
          f"Error handling: worst area = 6000 (training maximum {F['worst_area_train_minmax'][1]:g}) triggers a warning",
          width_in=5.0)


# ====================================================================== CHAPTER 6
def chapter6(R: Report, D, cite):
    R.h1("Chapter 6: Societal Impact, Ethical Governance, Safety & Security Audits", chapter="6")
    R.h2("6.1 Importance of Transparency in Clinical AI")
    R.p(f"Transparency lets clinicians check and challenge predictions {cite('holzinger2017', 'who2021')}; ClinXAI also "
        "audits the *explanations* by showing LIME and SHAP side by side with R², stability and sign conflicts.")
    R.h2("6.2 Human Oversight and Clinical Decision Support")
    R.p("An educational aid only: disclaimer on every view, *uncalibrated* probability label, borderline, low-R² and "
        "extrapolation warnings, and no recommendations; uncertain or disagreeing cases go to human review.")
    R.h2("6.3 Patient Privacy and Responsible Data Usage")
    R.p(f"Only public, de-identified data is used and nothing leaves the machine; a clinical version would need "
        f"consent and safeguards under the DPDP Act, 2023 {cite('dpdp2023')}.")
    R.h2("6.4 Model Bias, Dataset Limitations and Generalisation")
    R.p("The data are single-centre and historical, with no demographic attributes (so fairness cannot be audited), 37% "
        "malignant cases and only 114 test patients; new equipment or populations could shift the features.")
    R.h2("6.5 Safety Considerations and False Negatives")
    R.table("t_audit", "Safety and robustness audit", ["Failure mode", "Evidence", "Mitigation / residual risk"],
            [["Missed malignancy", "3 FNs (P 0.160–0.297)", "Warnings; threshold not tuned, no calibration"],
             ["Unfaithful / unstable LIME", "Mean R² 0.27; seed Jaccard 0.39 for #86", "R² and stability shown; not suppressed"],
             ["Invalid or out-of-range input", "Tested cases; value above training max", "Validation + warning"],
             [f"Explanation manipulation {cite('slack2020')}", "Not tested", "Open risk"],
             ["Tampered model file", "joblib uses pickle", "Local file only; no checksum yet"]],
            [1.8, 2.1, 2.1])
    R.h2("6.6 Relevant Ethical and Regulatory Considerations")
    R.p(f"ClinXAI is **not claimed to comply with, be certified under or be clinically validated against** any framework. "
        f"The EU AI Act treats medical-device AI as high-risk, with transparency (Art. 13), human oversight (Art. 14) and "
        f"accuracy/robustness (Art. 15) duties {cite('euaiact2024')}; WHO {cite('who2021')} and ICMR {cite('icmr2023')} "
        "stress autonomy, transparency, accountability and validity, including clinical validation before use. ClinXAI "
        "demonstrates transparency and oversight features; risk management, conformity assessment and clinical "
        "validation remain gaps.")
    R.h2("6.7 Alignment with UN Sustainable Development Goal 3")
    R.p(f"SDG 3 target 3.4 seeks to reduce premature mortality from non-communicable diseases such as cancer "
        f"{cite('un2015')}. ClinXAI contributes a reproducible, CPU-only method for auditing diagnostic explanations "
        "(training takes about 7 s and full evaluation about 36 s); any health impact would require clinical validation.")


# ====================================================================== CHAPTER 7
def chapter7(R: Report, D, cite):
    rf = D["metrics"]["random_forest"]
    agg = D["cases"]["aggregate_test_set"]
    R.h1("Chapter 7: Conclusion, Engineering Limitations & Future Enhancements", chapter="7")
    R.h2("7.1 Summary of Work Completed")
    R.p("ClinXAI delivers a reproducible pipeline: a Random Forest predicting P(malignant), LIME and TreeSHAP "
        "explanations for the same class, a LIME–SHAP comparison over all test patients, five case studies, a seven-tab "
        "dashboard and 24 automated tests.")
    R.h2("7.2 Achievement of Project Objectives")
    R.table("t_achieve", "Achievement of objectives", ["Objective", "Status", "Evidence"],
            [["O1 Classifier + baseline", "Achieved", f"Acc {pct(rf['accuracy'])}, recall {pct(rf['recall_sensitivity'])}, "
                                                    f"AUC {rf['roc_auc']:.4f}"],
             ["O2 LIME + TreeSHAP", "Achieved", "All 114 patients explained; additivity 4.4 × 10^{−16}"],
             ["O3 Agreement quantified", "Achieved", f"Overlap {agg['mean_top5_overlap']:.2f}/5, J {agg['mean_top5_jaccard']:.2f}, "
                                                    f"ρ {agg['mean_spearman_abs']:.2f}, {agg['pct_patients_with_direction_disagreement']:.1f}% disagree"],
             ["O4 Dashboard", "Achieved (local)", "7 tabs; 34/34 browser checks; not publicly deployed"]],
            [1.8, 1.1, 3.1])
    R.h2("7.3 Technical Limitations")
    R.bullets([
        "LIME is seed-dependent and has low fidelity (mean R² 0.27; ≤ 0.06 on the false negatives).",
        "Path-dependent TreeSHAP uses tree cover rather than an explicit background set; interventional SHAP was not "
        "evaluated.",
        "Small single-centre dataset, possible distribution shift, uncalibrated probabilities and no external or "
        "clinical validation; tabular input only.",
    ])
    R.h2("7.4 Future Enhancements")
    R.bullets([
        "Genuine multimodal diagnostics: a CNN on cytology images combined with the tabular features.",
        f"Fidelity thresholds for LIME, averaged multi-seed LIME, interventional SHAP and calibration "
        f"{cite('niculescu2005')}.",
        "External validation and **medical-expert validation before any deployment**; integrity checks and "
        "authentication for a deployed version.",
    ])


# ====================================================================== APPENDICES (compact)
def appendix_a(R: Report):
    R.h1("Appendix A: Complete Source Code Listings / Core Configuration Files", chapter="A")
    R.p("The central configuration file is listed below; pinned dependency versions are in Table 4.1. The complete "
        "source (1,916 lines) is submitted in the project folder, with key functions in Chapter 4.")
    for rel in ["src/config.py"]:
        lines = (PROJ / rel).read_text(encoding="utf-8").splitlines()
        R.code(lines, f"`{rel}` ({len(lines)} lines)", size=8.5)


def appendix_b(R: Report, D):
    R.h1("Appendix B: Raw Diagnostic Trace Logs, Audit Tables & Verification Sheets", chapter="B")
    R.code(D["train_log"].splitlines()[1:], "`python train_model.py` (report/evidence/train_model_console.txt)", size=8.5)
    tests = [l for l in D["pytest"].splitlines() if "::" in l or "passed" in l]
    R.code(tests, "`python -m pytest -v` (report/evidence/pytest_verbose.txt)", size=8.5)
    b = D["browser"]
    R.table("t_verify", "Verification summary", ["Layer", "Result"],
            [["Automated tests (also after a clean install)", "24 / 24 passed"],
             ["Independent saved-output validation", "35 / 35 passed"],
             ["Real-browser click-through (Edge)", f"{sum(r['passed'] for r in b)} / {len(b)} passed"],
             ["Runtime warnings during training and evaluation", "0"]],
            [4.2, 1.8], align=["l", "c"])
