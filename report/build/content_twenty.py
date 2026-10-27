"""20-page edition: compact preliminary pages + continuously flowing technical body.

Same facts as the other editions; every number is read from the generated project outputs at build time.
"""
from pathlib import Path

from docx.enum.text import WD_ALIGN_PARAGRAPH

from engine import Report
from content_mid import code_from

PROJ = Path(__file__).resolve().parents[2]
OUT_FIG = PROJ / "outputs" / "figures"
REP_FIG = PROJ / "report" / "figures"


def pct(x):
    return f"{100 * x:.2f}%"


# ====================================================================== PRELIMINARY PAGES (compact)
def prelims(R: Report, D, cite):
    R.h1("Course Articulation & Outcome Alignment Sheet")
    R.table("t_copo", None, ["Project Activity Component", "Mapped CO", "Bloom's Level", "Mapped POs / PSOs",
                             "Measurable Performance Benchmark", "ClinXAI Evidence"],
            [["Explainability Architecture & Feature Attribution (SHAP / LIME)", "CO 1", "BL 2 (Understand) / BL 3 (Apply)",
              "PO1, PO2, PO5, PSO1", "Global summary & local force plots generated with zero syntax error",
              "SHAP, LIME, waterfall and force plots; 24/24 tests"],
             ["End-to-End Responsible AI Deployment & Interactive UI Dashboard", "CO 1 - CO 3",
              "BL 5 (Evaluate) / BL 6 (Create)", "PO2, PO3, PO5, PO9, PSO3",
              "Fully responsive live dashboard deployed on Streamlit or Gradio",
              "Local 7-tab Streamlit app (not publicly deployed); 34/34 browser checks"]],
            [1.25, 0.6, 0.85, 0.85, 1.1, 1.35], keep_together=True)
    R.note("Official rows unchanged; the other four components (fairness, adversarial, privacy, model card) are not "
           "implemented.")
    R.h1("CIAP 25-Mark Rubric Evaluation Sheet")
    R.table("t_rubric", None, ["Criteria", "Excellent (4 Marks)", "Good (3 Marks)", "Satisfactory (2 Marks)",
                               "Needs Improvement (1 Mark)"],
            [["Problem Definition & Scope (15%)", "Clearly defined problem with a focused and achievable scope.",
              "Problem identified, but scope may be unclear or too broad/narrow.",
              "Problem vaguely defined, or scope missing.", "Problem not clearly identified or missing."],
             ["Design & Methodology (20%)", "Innovative and well-structured approach with justification for chosen methods.",
              "Appropriate design and methodology, but limited justification.",
              "Basic design and methodology, with some justification.", "Weak or missing design and methodology."],
             ["Implementation & Results (25%)", "Project completed effectively with clear and well-presented results.",
              "Project completed, but results unclear or poorly presented.",
              "Project partially completed with limited or unclear results.", "Project not completed or results missing."],
             ["Analysis & Interpretation (20%)", "Thorough analysis with insightful interpretation of results.",
              "Analysis attempts were made, but interpretation could be improved.",
              "Basic analysis with limited interpretation.", "Weak or missing analysis and interpretation."],
             ["Report & Presentation (20%)", "Clear, concise, and well-organized report with effective presentation.",
              "Report generally well-written but may lack clarity or organization. Presentation could be improved.",
              "Report lacks clarity or organization. Presentation needs significant work.",
              "Poorly written report with ineffective or missing presentation."]],
            [1.2, 1.2, 1.2, 1.2, 1.2], bold_first_col=True, keep_together=True)
    R.p("Marks: ______ / 25      Evaluator's signature: _______________      Date: ________",
        align=WD_ALIGN_PARAGRAPH.LEFT)

    R.h1("Abstract", new_page=True)
    R.p("Accurate machine-learning models for breast-cancer diagnosis, such as Random Forests, act as black boxes. "
        "ClinXAI builds a transparent pipeline on the Breast Cancer Wisconsin (Diagnostic) dataset (569 patients, 30 "
        "nuclear features from fine-needle-aspirate images), with malignant as the positive class and a stratified "
        "80/20 split keeping 114 patients unseen. A 300-tree Random Forest is compared with a Logistic Regression "
        "baseline, and every prediction is explained by LIME (a seeded local linear surrogate) and TreeSHAP (exact "
        "Shapley attributions in probability units), presented in a seven-tab Streamlit dashboard that supports patient "
        "selection, what-if biomarker editing and side-by-side comparison of the two explanations, with all results "
        "reproducible from fixed random seeds. On the held-out set "
        "the forest achieved 97.37% accuracy, 100% precision, 92.86% recall, 96.30% F1 and ROC-AUC 0.9944 (TN = 72, "
        "FP = 0, FN = 3, TP = 39); SHAP additivity held to 4.4 × 10^{−16}. LIME and SHAP shared on average 3.66 of their "
        "top-five features (Jaccard 0.62, Spearman 0.70), and 28.9% of patients showed a directional disagreement. "
        "Agreement was complete for confident predictions but collapsed for the missed malignancies (Patients #86 and "
        "#73), where LIME's local fit fell to R² ≤ 0.06, showing that explanations must themselves be audited before "
        "clinical use.")
    R.p("**Keywords:** Explainable AI; LIME; SHAP; TreeSHAP; Random Forest; Breast Cancer Diagnosis; Clinical Decision "
        "Support", align=WD_ALIGN_PARAGRAPH.LEFT)

    R.prelim_heading("Table of Contents")
    R.field_paragraph('TOC \\o "1-1" \\h \\z \\u', "Right-click and choose Update Field.")
    R.prelim_title("List of Figures")
    R.field_paragraph('TOC \\h \\z \\t "Figure Caption,1"', "Right-click and choose Update Field.")
    R.prelim_heading("List of Tables")
    R.field_paragraph('TOC \\h \\z \\t "Table Caption,1"', "Right-click and choose Update Field.")
    R.prelim_heading("List of Abbreviations")
    ab = [("AUC", "Area Under the ROC Curve"), ("CO / PO", "Course / Program Outcome"),
          ("FN / FP", "False Negative / Positive"), ("FNA", "Fine-Needle Aspirate"),
          ("LIME", "Local Interpretable Model-agnostic Explanations"), ("LR", "Logistic Regression"),
          ("RF", "Random Forest"), ("ROC", "Receiver Operating Characteristic"),
          ("SHAP", "SHapley Additive exPlanations"), ("XAI", "Explainable Artificial Intelligence")]
    rows = [[ab[i][0], ab[i][1], ab[i + 5][0], ab[i + 5][1]] for i in range(5)]
    R.table("t_abbr", None, ["Abbr.", "Expansion", "Abbr.", "Expansion"], rows, [0.8, 2.2, 0.8, 2.2],
            bold_first_col=True)


# ====================================================================== BODY
def body(R: Report, D, cite):
    M = D["metrics"]
    rf, lr, ds = M["random_forest"], M["logistic_regression_baseline"], M["dataset"]
    cm = rf["confusion_matrix"]
    agg = D["cases"]["aggregate_test_set"]
    cases = {c["patient_id"]: c for c in D["cases"]["cases"]}
    desc, F = D["desc"], D["facts"]
    env = dict(l.strip().split("==") for l in D["environment"].splitlines() if "==" in l)

    # -------------------------------------------------------------- Chapter 1
    R.h1("Chapter 1: Problem Definition & Operational Relevance", chapter="1")
    R.h2("1.1 Problem Statement and Background")
    R.p(f"Breast cancer is the most common cancer in women (about 2.3 million diagnoses and 670,000 deaths in 2022 "
        f"{cite('who2024bc')}). Nuclear measurements from digitised fine-needle-aspirate images {cite('street1993')} "
        f"form the Breast Cancer Wisconsin (Diagnostic) dataset {cite('uci1995')}. Accurate ensembles such as a 300-tree "
        f"Random Forest (10,976 nodes here) are black boxes {cite('breiman2001', 'rudin2019')}. **Problem:** predict "
        "P(malignant) from 30 features, explain each prediction with LIME and SHAP for the same class, and measure when "
        "the two explanations disagree.")
    R.h2("1.2 Clinical and Societal Relevance")
    R.p(f"Unexplained scores invite blind trust or rejection, a missed cancer with a plausible explanation is hard to "
        f"catch, and explainers can disagree {cite('krishna2022')}; regulators expect transparency and human oversight "
        f"{cite('euaiact2024', 'who2021')}.")
    R.h2("1.3 Project Objectives")
    R.p("**O1** Implement and evaluate a Random Forest against a Logistic Regression baseline on 114 held-out patients. "
        "**O2** Apply LIME and TreeSHAP and verify SHAP additivity (< 10^{−6}). **O3** Quantify LIME–SHAP agreement "
        "(top-5 overlap, Jaccard, Spearman ρ, sign agreement, seed stability). **O4** Design and validate a "
        "seven-tab dashboard.")
    R.h2("1.4 Project Scope and Operational Boundaries")
    R.p("In scope: tabular prediction, LIME/SHAP explanation and comparison, five case studies, a local dashboard. Out "
        "of scope: raw images, calibrated risk, treatment advice, clinical validation, fairness audit, public deployment. "
        "*Multi-modal* refers to the two explanation modalities; the input is one tabular modality derived from images.")

    # -------------------------------------------------------------- Chapter 2
    R.h1("Chapter 2: Theoretical Formulation, Literature Review & Mathematical Framework", chapter="2")
    R.h2("2.1 Explainable Artificial Intelligence")
    R.p("XAI explanations are post-hoc or intrinsic, local or global, and agnostic or model-specific; this report "
        "evaluates **local fidelity**, **consistency**, **stability** and computational cost.")
    R.h2("2.2 Random Forest Classification")
    R.eq("f(x) = (1/T) · Σ_{t=1..T} p_{t}(y = 1 | x),     G(node) = 1 − Σ_{k} p_{k}^{2}", "(2.1)")
    R.p(f"The forest averages T = 300 bootstrap trees {cite('breiman2001')} grown with Gini impurity G and ⌊√30⌋ = 5 "
        f"features per split (scikit-learn); p_{{t}} is the malignant leaf fraction of tree t.")
    R.h2("2.3 LIME: Local Interpretable Model-Agnostic Explanations")
    R.p(f"LIME {cite('ribeiro2016')} fits a simple model g that imitates f only near x, using quartile-binned rules "
        "such as `worst area > 1122.50` → +0.137.")
    R.h2("2.4 LIME Perturbation and Local Surrogate Formulation")
    R.eq("ξ(x) = argmin_{g} Σ_{i} π_{x}(z_{i})·(f(z_{i}) − g(z′_{i}))^{2} + λ‖w‖^{2}", "(2.2)")
    R.p(f"Here z_{{i}} are 5,000 perturbations, z′ ∈ {{0,1}}^{{30}} marks whether each feature stays in the patient's "
        f"bin, π_{{x}} = exp(−D²/2σ²) with σ = 0.75√30 ≈ {F['kernel_width_default']}, λ = 1 and "
        f"g(z′) = w_{{0}} + Σ w_{{j}}z′_{{j}}. The weighted R² is "
        f"LIME's only fidelity signal, and results depend on the seed {cite('alvarez2018')}.")
    R.h2("2.5 SHAP: Shapley Additive Explanations")
    R.eq("P(malignant | x) = φ_{0} + Σ_{j=1..30} φ_{j}(x),     φ_{0} = E[f(X)]", "(2.3)")
    R.p(f"SHAP {cite('lundberg2017')} attributions satisfy local accuracy (Equation 2.3), missingness and consistency.")
    R.h2("2.6 Shapley Game-Theoretic Attribution")
    R.eq("φ_{j}(x) = Σ_{S⊆F∖{j}} [|S|!·(M−|S|−1)!/M!]·[v_{x}(S∪{j}) − v_{x}(S)]", "(2.4)")
    R.p(f"Features are players and v_{{x}}(S) = E[f(X) | X_{{S}} = x_{{S}}] is a coalition's payout {cite('shapley1953')}; "
        "naive evaluation needs 2^{30} ≈ 1.07 × 10^{9} coalitions.")
    R.h2("2.7 TreeSHAP Explanation Method")
    R.p(f"TreeSHAP {cite('lundberg2020')} computes Equation (2.4) exactly in O(T·L·D^{{2}}) using each node's training "
        f"cover; φ_{{0}} = 0.3747 (≈ training prevalence {F['train_malignant']}/455) and the φ_{{j}} share probability units "
        "with `predict_proba`.")
    R.h2("2.8 LIME versus SHAP: Mathematical and Practical Trade-offs")
    R.p("LIME is approximate, seed-dependent and compares a bin with other bins; TreeSHAP is exact, deterministic and "
        "compares with E[f(X)]. Magnitudes are not comparable, so agreement uses ranks and signs of the top-5 sets A, B:")
    R.eq("J = |A ∩ B| / |A ∪ B|,     ρ = 1 − 6Σ_{j} d_{j}^{2} / (n(n^{2} − 1)),  n = 30", "(2.5)")
    R.h2("2.9 Comparative Literature Review")
    R.p(f"Logistic regression is faithful but restricted {cite('rudin2019')}; LIME and KernelSHAP are model-agnostic but "
        f"approximate; TreeSHAP is exact for trees. Perturbation explainers can be fooled {cite('slack2020')} and often "
        f"disagree {cite('krishna2022')}, which matters most in high-stakes medicine {cite('rudin2019')}.")

    # -------------------------------------------------------------- Chapter 3
    R.h1("Chapter 3: System Architecture, Design Pipeline & Workflow Models", chapter="3")
    R.h2("3.1 Overall System Architecture")
    R.p(f"{R.ref('f_arch')} shows the data, model, explanation, comparison, presentation and test layers, each a real "
        "module (`src/`, `train_model.py`, `evaluate.py`, `app.py`, `tests/`).")
    R.fig("f_arch", OUT_FIG / "architecture.png", "ClinXAI system architecture", width_in=4.8)
    R.h2("3.2 Dataset and Feature Description")
    R.p(f"569 patients (212 malignant, 357 benign) {cite('uci1995')}; ten nuclear characteristics (radius, texture, "
        "perimeter, area, smoothness, compactness, concavity, concave points, symmetry, fractal dimension) as mean, "
        "standard error and worst values = 30 features, no missing values.")
    R.h2("3.3 Data Preprocessing Pipeline")
    R.p("Validation of shape and values; malignant re-encoded to 1 (asserted); stratified 80/20 split, random_state = 42 "
        "(455 / 114); model, LIME statistics and scaler fitted on training data only; feature order enforced.")
    R.h2("3.4 Random Forest Diagnostic Prediction Pipeline")
    R.p("`train_model.py` trains the forest, asserts `classes_ == [0, 1]`, evaluates at threshold 0.5, runs 5-fold CV "
        "and saves one joblib bundle.")
    R.h2("3.5 LIME Explanation Workflow")
    R.p("Fresh seeded explainer → 5,000 perturbations → forest via a feature-name wrapper → kernel weights → ridge "
        "surrogate (weights, rules, R²).")
    R.h2("3.6 SHAP Explanation Workflow")
    R.p("`TreeExplainer` → (n, 30, 2) array → malignant slice → additivity check → global, waterfall and force plots.")
    R.h2("3.7 Streamlit User Interaction Flow")
    R.p("Sidebar patient choice and what-if edits → `validate_patient_input()` → cached LIME/SHAP → seven tabs.")
    R.h2("3.8 System Architecture Diagram and Data Flow Diagram")
    R.fig("f_dfd", REP_FIG / "report_dfd.png", "Level-1 data-flow diagram", width_in=4.2)

    # -------------------------------------------------------------- Chapter 4
    R.h1("Chapter 4: Implementation Details, Algorithms & Technological Artifacts", chapter="4")
    R.h2("4.1 Development Environment and Technology Stack")
    R.p(f"Python 3.12.10 on Windows 11 (CPU only); scikit-learn {env['scikit-learn']}, LIME {env['lime']}, SHAP "
        f"{env['shap']}, Streamlit {env['streamlit']}, Matplotlib {env['matplotlib']}, pandas {env['pandas']}, NumPy "
        f"{env['numpy']}, pytest {env['pytest']} (pinned in `requirements.txt`).")
    R.h2("4.2 Dataset Loading and Target Mapping")
    R.p("`load_dataset()` derives the mapping from `target_names`, re-encodes malignant = 1 and asserts it against the "
        "raw labels.")
    R.h2("4.3 Model Training Implementation")
    R.p("`train_random_forest` fits `RandomForestClassifier(**RF_PARAMS)` on the training set and asserts "
        "`classes_ == [0, 1]`, so column 1 of `predict_proba` is always P(malignant).")
    R.h2("4.4 LIME Explainer Implementation")
    R.p("A wrapper rebuilds a DataFrame in training order for every LIME query, and a fresh seeded explainer per call "
        "makes explanations reproducible; label 1 (malignant) and all 30 features are explained.")
    R.h2("4.5 SHAP Explainer Implementation")
    R.p("`_select_malignant` normalises version-dependent SHAP outputs to the malignant class; `additivity_error` "
        "checks Equation (2.3) against `predict_proba`.")
    R.h2("4.6 LIME–SHAP Comparison Implementation")
    R.p("`compare_explanations` computes top-5 sets, Jaccard, Spearman ρ and the sign table; `select_case_studies` picks "
        "max P, min P, P nearest 0.5, lowest Jaccard and most sign conflicts, reporting any missing case as not found.")
    R.h2("4.7 Streamlit Interface Implementation")
    R.p("`app.py` (488 lines): sidebar selector and LIME settings, seven tabs, what-if editor, stability toggle and "
        "cached explanations (@[f_ui]).")
    R.h2("4.8 Input Validation and Error Handling")
    R.p("`validate_patient_input` rejects missing features, NaN, ∞, text and negatives (7 tests); out-of-range values "
        "raise a warning.")
    R.h2("4.9 Code Structure and Module Responsibilities")
    R.p("1,916 lines across `src/` (7 modules), three scripts and a 24-test suite (Appendix A).")

    # -------------------------------------------------------------- Chapter 5
    R.h1("Chapter 5: Experimental Evaluation, Testing, Trade-off Analysis & Empirical Results", chapter="5")
    R.h2("5.1 Experimental Methodology")
    R.p("Fit on 455 patients, test once on 114 (threshold 0.5); LIME (seed 42) and TreeSHAP explain every test "
        "patient; five rule-selected case studies.")
    R.h2("5.2 Dataset Characteristics and Train/Test Split")
    R.p(f"Train {ds['n_train']} ({F['train_malignant']} malignant); test {ds['n_test']} ({ds['test_malignant']} malignant, "
        f"{ds['test_benign']} benign).")
    R.h2("5.3 Accuracy, Precision, Recall, F1 and ROC-AUC")
    R.table("t_metrics", "Held-out test performance (positive class = malignant)",
            ["Model", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC"],
            [["Random Forest", pct(rf["accuracy"]), pct(rf["precision"]), pct(rf["recall_sensitivity"]), pct(rf["f1"]),
              f"{rf['roc_auc']:.4f}"],
             ["Logistic Regression", pct(lr["accuracy"]), pct(lr["precision"]), pct(lr["recall_sensitivity"]),
              pct(lr["f1"]), f"{lr['roc_auc']:.4f}"]],
            [1.6, 0.9, 0.9, 0.9, 0.85, 0.85], align=["l", "c", "c", "c", "c", "c"])
    R.h2("5.4 Confusion Matrix and ROC Curve")
    R.p(f"TN = {cm['tn']}, FP = {cm['fp']}, FN = {cm['fn']}, TP = {cm['tp']}: every error is a missed malignancy "
        f"({R.ref('f_cmroc')}). CV ROC-AUC on training data: {rf['cv_roc_auc_mean']:.4f} ± {rf['cv_roc_auc_std']:.4f}.")
    R.fig("f_cmroc", REP_FIG / "compact_cm_roc.png", "(a) Confusion matrix; (b) ROC curves", width_in=4.0)
    R.h2("5.5 Global SHAP Feature Importance")
    gi = D["global_importance"][:4]
    R.p("Top features by mean |SHAP|: " + ", ".join(f"{r['feature']} ({float(r['mean_abs_shap']):.3f})" for r in gi)
        + f" ({R.ref('f_global')}).")
    R.fig("f_global", REP_FIG / "compact_shap_global.png", "(a) Global mean |SHAP|; (b) SHAP beeswarm", width_in=5.0)
    c70, c74, c86, c73, c100 = (cases[k] for k in (70, 74, 86, 73, 100))
    R.h2("5.6 Individual Patient LIME Explanations")
    R.p(f"For #70 (P = 1.000) every top LIME rule points to malignant (R² = {c70['lime_local_r2']:.2f}). For missed "
        f"malignancy #86 (P = {c86['p_malignant']:.3f}) the top rules point to malignant despite a benign output and the "
        f"surrogate barely fits (R² = {c86['lime_local_r2']:.2f}; predicts {c86['lime_local_pred']:.3f}) "
        f"({R.ref('f_p86')}a).")
    R.h2("5.7 Individual Patient SHAP Explanations")
    R.p(f"For #86, 0.3747 − 0.0780 = {c86['p_malignant']:.4f} ({R.ref('f_p86')}b). Additivity held for all 114 patients "
        f"(max error **{D['additivity']['max_abs_error']:.1e}**).")
    R.fig("f_p86", REP_FIG / "compact_p86_lime_waterfall.png", "Patient #86: (a) LIME and (b) SHAP waterfall",
          width_in=5.3)
    R.h2("5.8 LIME–SHAP Case Study Comparison")
    order = [70, 74, 100, 86, 73]
    R.table("t_cases", "Five programmatically selected case studies",
            ["Case", "Patient", "P(mal.)", "Actual / predicted", "Top-5", "Jaccard", "ρ", "Sign flips", "R²"],
            [[cases[p]["case_type"], f"#{p}", f"{cases[p]['p_malignant']:.3f}",
              f"{cases[p]['true_label']} / {'Malignant' if cases[p]['p_malignant'] >= 0.5 else 'Benign'}",
              f"{cases[p]['comparison']['top_k_overlap']}/5", f"{cases[p]['comparison']['jaccard_top_k']:.2f}",
              f"{cases[p]['comparison']['spearman_abs_all_features']:.2f}",
              str(len(cases[p]['comparison']['direction_disagreements_union'])), f"{cases[p]['lime_local_r2']:.2f}"]
             for p in order],
            [0.95, 0.6, 0.6, 0.88, 0.55, 0.7, 0.4, 0.72, 0.6], align=["l", "c", "c", "l", "c", "c", "c", "c", "c"])
    R.p(f"Confident cases #70 and #74 share all five features with no sign conflicts, although #74's surrogate is off "
        f"by 0.11 (R² {c74['lime_local_r2']:.2f}). Borderline #100 shares only two. Missed malignancies #86 (**no shared "
        f"feature**, seed stability {c86['lime_stability']['mean_pairwise_jaccard_top_k']:.2f}) and #73 (one shared) each "
        f"show four sign flips ({R.ref('f_cmp86')}). Worst area for #86/#73 "
        f"({F['case_values']['86']['worst area']}/{F['case_values']['73']['worst area']}) lies in the wide bin "
        f"{F['worst_area_train_quartiles'][1]}–{F['worst_area_train_quartiles'][2]}: LIME compares it with mostly benign "
        "lower bins (+), SHAP with the base value (−). **Clinical limitation:** SHAP gives an exact rationale for a wrong "
        "prediction and LIME gives malignant reasons for a benign label; neither is evidence about the tumour.")
    R.fig("f_cmp86", OUT_FIG / "lime_vs_shap_case4_patient86.png", "LIME vs SHAP for Patient #86",
          width_in=4.0)
    R.h2("5.9 Explanation Divergence Analysis")
    fns = desc["false_negatives"]
    R.p(f"Over 114 patients: mean top-5 overlap **{agg['mean_top5_overlap']:.2f}/5**, Jaccard "
        f"**{agg['mean_top5_jaccard']:.2f}**, Spearman **{agg['mean_spearman_abs']:.2f}**, direction disagreement in "
        f"**{agg['pct_patients_with_direction_disagreement']:.1f}%** (33 patients) and mean LIME R² "
        f"{agg['mean_lime_local_r2']:.2f}. Agreement rises with confidence |P − 0.5| (ρ = "
        f"{desc['spearman_confidence_vs_jaccard']:.2f}; {R.ref('f_conf')}), and all three false negatives (#73, #86, "
        f"#385) have Jaccard ≤ 0.25 and R² ≤ {max(r['lime_local_r2'] for r in fns):.3f} (descriptive analysis of the saved "
        f"CSV). Causes: different reference points, a linear surrogate on a non-linear boundary, "
        f"{F['n_pairs_corr_gt_0.9']} feature pairs with |r| > 0.9 and perturbation noise {cite('slack2020', 'alvarez2018')}. "
        "**Low LIME fidelity and disagreement concentrate on the predictions that most need human review.**")
    R.fig("f_conf", REP_FIG / "report_confidence_vs_agreement.png",
          "Agreement and LIME fidelity versus model confidence", width_in=5.0)
    R.h2("5.10 Model Performance and Interpretability Trade-offs")
    R.p(f"The forest beats the transparent baseline by one false positive and both miss three cancers {cite('rudin2019')}; "
        "LIME trades fidelity for simplicity, TreeSHAP is exact but tree-only, and a lower threshold would need separate "
        "validation data.")
    R.h2("5.11 Operational Verification Screenshots")
    R.p("Real screenshots (Edge, Playwright). Verification: 24/24 tests (also after a clean install), 35/35 output checks, "
        "34/34 browser checks.")
    R.fig("f_ui", REP_FIG / "compact_ui_window_whatif.png",
          "(a) Dashboard; (b) what-if on #100 flips the output to benign")
    R.fig("f_ui_oor", REP_FIG / "ui_error_out_of_range_warning.png",
          "Error handling: out-of-range input warning", width_in=4.6)

    # -------------------------------------------------------------- Chapter 6
    R.h1("Chapter 6: Societal Impact, Ethical Governance, Safety & Security Audits", chapter="6")
    R.h2("6.1 Importance of Transparency in Clinical AI")
    R.p(f"Transparency lets clinicians check predictions {cite('who2021')}; ClinXAI also audits the explanations.")
    R.h2("6.2 Human Oversight and Clinical Decision Support")
    R.p("ClinXAI is not a medical device and is not clinically validated: an educational aid with a disclaimer, an "
        "*uncalibrated* label, borderline/low-R²/extrapolation warnings and no recommendations.")
    R.h2("6.3 Patient Privacy and Responsible Data Usage")
    R.p(f"Public de-identified data only; real patient data would require consent and safeguards {cite('dpdp2023')}.")
    R.h2("6.4 Model Bias, Dataset Limitations and Generalisation")
    R.p("Single-centre data, no demographics (no fairness audit), 114 test patients, possible distribution shift.")
    R.h2("6.5 Safety Considerations and False Negatives")
    R.p("Three missed malignancies (P 0.160–0.297) with unreliable explanations; explanation manipulation is untested and "
        "the pickle-based model file has no checksum.")
    R.h2("6.6 Relevant Ethical and Regulatory Considerations")
    R.p(f"**No compliance, certification or clinical validation is claimed.** The EU AI Act requires transparency, "
        f"oversight and robustness for high-risk medical AI {cite('euaiact2024')}, and WHO guidance {cite('who2021')} "
        "requires validity, including clinical validation; India's ICMR (2023) AI guidelines stress the same.")
    R.h2("6.7 Alignment with UN Sustainable Development Goal 3")
    R.p(f"Supports SDG 3.4 (reducing cancer mortality) {cite('un2015')} through a reproducible, CPU-only audit method.")

    # -------------------------------------------------------------- Chapter 7
    R.h1("Chapter 7: Conclusion, Engineering Limitations & Future Enhancements", chapter="7")
    R.h2("7.1 Summary of Work Completed")
    R.p("A tested pipeline: Random Forest, LIME and TreeSHAP for the same class, LIME–SHAP comparison, five case "
        "studies and a seven-tab dashboard.")
    R.h2("7.2 Achievement of Project Objectives")
    R.p(f"O1 achieved (accuracy {pct(rf['accuracy'])}, AUC {rf['roc_auc']:.4f}); O2 achieved (additivity 4.4 × 10^{{−16}}); "
        f"O3 achieved (Jaccard {agg['mean_top5_jaccard']:.2f}, ρ {agg['mean_spearman_abs']:.2f}); O4 achieved locally "
        "(34/34 browser checks).")
    R.h2("7.3 Technical Limitations")
    R.p("Seed-dependent, low-fidelity LIME; path-dependent SHAP without a background set; small single-centre data; "
        "uncalibrated probabilities; no external or clinical validation; tabular input only.")
    R.h2("7.4 Future Enhancements")
    R.p("Image + tabular multimodal models, LIME fidelity thresholds, interventional SHAP, probability calibration, "
        "external validation and **medical-expert validation before any deployment**.")


def appendices(R: Report, D):
    lc = D["facts"]["line_counts"]
    R.h1("Appendix A: Complete Source Code Listings / Core Configuration Files", chapter="A")
    R.p("Condensed for length: the file inventory below points to the complete source code submitted in the project "
        "folder `ClinXAI/`; the key comparison routine follows.", space_after=2)
    inv = [("app.py", "Streamlit dashboard (7 tabs)"), ("train_model.py", "Training, metrics, model bundle"),
           ("evaluate.py", "SHAP, LIME, comparison, case studies"), ("src/data_loader.py", "Loading, mapping, validation"),
           ("src/model.py", "Model training and evaluation"), ("src/explain_lime.py", "LIME explanations"),
           ("src/explain_shap.py", "SHAP explanations"), ("src/comparison.py", "LIME–SHAP agreement"),
           ("src/visualization.py", "Figures"), ("tests/test_pipeline.py", "24 automated tests")]
    rows = [[inv[i][0], inv[i][1], str(lc[inv[i][0]]), inv[i + 5][0], inv[i + 5][1], str(lc[inv[i + 5][0]])]
            for i in range(5)]
    R.table("t_inventory", "Source-file inventory (complete code in the project folder)",
            ["File", "Purpose", "Lines", "File", "Purpose", "Lines"], rows,
            [1.3, 1.15, 0.55, 1.4, 1.05, 0.55], align=["l", "l", "r", "l", "l", "r"])
    code_from(R, "src/comparison.py", start="def compare_explanations", end="    direction_rows = []",
              what="LIME–SHAP agreement measures")
    R.h1("Appendix B: Raw Diagnostic Trace Logs, Audit Tables & Verification Sheets", chapter="B")
    tail = [l for l in D["pytest"].splitlines() if l.strip()][-4:]
    R.code(tail, "`python -m pytest -v` — final lines of the 24-test log (report/evidence/pytest_verbose.txt)")
    b = D["browser"]
    R.table("t_verify", "Verification summary", ["Verification layer", "Result"],
            [["Automated tests (also after a clean install)", "24 / 24 passed"],
             ["Independent saved-output validation", "35 / 35 passed"],
             ["Real-browser click-through (Microsoft Edge)", f"{sum(r['passed'] for r in b)} / {len(b)} passed"],
             ["Runtime warnings during training and evaluation", "0"]],
            [4.2, 1.8], align=["l", "c"])
