"""Preliminary pages (after the template pages), Chapter 1 and Chapter 2."""
from docx.enum.text import WD_ALIGN_PARAGRAPH

from engine import Report


def prelims(R: Report, D: dict, cite):
    m = D["metrics"]["random_forest"]
    agg = D["cases"]["aggregate_test_set"]

    # ------------------------------------------------------------ CO / PO / PSO alignment sheet
    R.h1("Course Articulation & Outcome Alignment Sheet")
    R.p("This sheet maps the ClinXAI micro-project to the Course Outcome alignment template supplied in the official "
        "*Technical Micro-Project Report Guidelines* for Trustworthy and Responsible AI (ADCOR1PC303), Section 4 "
        "(NBA SAR Criterion 3). The first five columns reproduce the official template text unchanged. The last two "
        "columns state whether each component applies to ClinXAI and give the evidence produced by this project.")
    rows = [
        ["Explainability Architecture & Feature Attribution (SHAP / LIME)", "CO 1", "BL 2 (Understand) / BL 3 (Apply)",
         "PO1, PO2, PO5, PSO1", "Global summary & local force plots generated with zero syntax error",
         "**Applicable — core of this project**",
         "Global SHAP bar and beeswarm plots; local LIME, waterfall and force plots for 5 case studies; "
         "SHAP additivity error 4.4 × 10^{−16}; 24/24 automated tests passed"],
        ["Fairness Audit & Debiasing Pipeline (Reweighing / Equalized Odds)", "CO 2", "BL 3 (Apply) / BL 4 (Analyze)",
         "PO1, PO2, PO3, PO5, PSO1", "Disparate impact improved >= 0.80; TPR gap minimized towards 0.00",
         "Not applicable", "Not implemented; the dataset has no demographic attributes (see Section 6.4)"],
        ["Adversarial Defense & Evasion Fortification (FGSM / Rob. Training)", "CO 3", "BL 4 (Analyze) / BL 5 (Evaluate)",
         "PO1, PO2, PO3, PO5, PSO2", "Adversarial training maintains > 60% accuracy under epsilon=0.20",
         "Not applicable", "Not implemented"],
        ["Privacy Vulnerability & Membership Inference Defense (MIA / DP)", "CO 3", "BL 4 (Analyze) / BL 5 (Evaluate)",
         "PO1, PO2, PO4, PO6, PSO2", "Shadow model attack accuracy audited; differential noise calibrated",
         "Not applicable", "Not implemented"],
        ["Legal Compliance Audit & AI Model Card Generation (DPDP / EU AI)", "CO 3", "BL 4 (Analyze) / BL 5 (Evaluate)",
         "PO2, PO6, PO7, PO8, PSO3", "Completed technical Model Card aligned with EU AI Act Annex III",
         "Not applicable as a deliverable",
         "No model card or compliance audit was produced; Chapter 6 discusses principles only"],
        ["End-to-End Responsible AI Deployment & Interactive UI Dashboard", "CO 1 - CO 3", "BL 5 (Evaluate) / BL 6 (Create)",
         "PO2, PO3, PO5, PO9, PSO3", "Fully responsive live dashboard deployed on Streamlit or Gradio",
         "**Applicable (explainability scope)**",
         "Seven-tab Streamlit dashboard run locally (`streamlit run app.py`); 34/34 real-browser checks passed. "
         "Not deployed to a public server; layout verified at desktop width only"],
    ]
    R.table("t_copo", None, ["Project Activity Component", "Mapped CO", "Bloom's Level", "Mapped POs / PSOs",
                             "Measurable Performance Benchmark", "Applicability to ClinXAI", "ClinXAI Evidence"],
            rows, [1.05, 0.5, 0.75, 0.75, 0.95, 0.8, 1.2], font_size=8, keep_together=False)
    R.note("Only the first and last rows apply to this project. For the dashboard row, ClinXAI covers the "
           "explainability outcomes (CO 1); it does not implement the CO 2 and CO 3 activities (fairness debiasing, "
           "adversarial defence, privacy attacks or a compliance model card).")

    # ------------------------------------------------------------ CIAP rubric (reproduced verbatim)
    R.h1("CIAP 25-Mark Rubric Evaluation Sheet")
    R.p("The assessment rubric below is reproduced verbatim from Section 5 of the official guidelines "
        "(*Standard 25-Mark CIAP Evaluation Rubric*). Marks are awarded by the assessment committee only.")
    rub = [
        ["Problem Definition & Scope (15%)", "Clearly defined problem with a focused and achievable scope.",
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
         "Poorly written report with ineffective or missing presentation."],
    ]
    R.table("t_rubric", None, ["Criteria", "Excellent (4 Marks)", "Good (3 Marks)", "Satisfactory (2 Marks)",
                               "Needs Improvement (1 Mark)"], rub, [1.2, 1.2, 1.2, 1.2, 1.2], font_size=9,
            bold_first_col=True)
    R.p("**Evaluation record (to be completed by the assessment committee)**", align=WD_ALIGN_PARAGRAPH.LEFT,
        space_after=2, keep_next=True)
    R.table("t_rubric_marks", None, ["Criteria", "Weight", "Level awarded (1–4)", "Marks awarded", "Remarks"],
            [["Problem Definition & Scope", "15%", "", "", ""], ["Design & Methodology", "20%", "", "", ""],
             ["Implementation & Results", "25%", "", "", ""], ["Analysis & Interpretation", "20%", "", "", ""],
             ["Report & Presentation", "20%", "", "", ""], ["**Total (CIAP — 25 Marks)**", "100%", "", "", ""]],
            [1.9, 0.7, 1.1, 1.0, 1.3], align=["l", "c", "c", "c", "l"], font_size=10)
    R.p("Evaluator's name and signature: ______________________________", align=WD_ALIGN_PARAGRAPH.LEFT,
        space_after=2)
    R.p("Date: ______________", align=WD_ALIGN_PARAGRAPH.LEFT)

    # ------------------------------------------------------------ abstract
    R.h1("Abstract")
    R.p("Machine-learning models can predict whether a breast tumour is malignant from cytology measurements with high "
        "accuracy. Ensembles such as Random Forests, however, behave as black boxes: the clinicians expected to act on "
        "a prediction cannot see why it was made. This micro-project, ClinXAI, builds and evaluates an end-to-end "
        "transparent diagnostic pipeline on the Breast Cancer Wisconsin (Diagnostic) dataset, which contains 569 patients "
        "and 30 numeric nuclear features computed from digitised fine-needle-aspirate images. Labels are re-encoded so "
        "that malignant is the positive class, and a stratified 80/20 split (random_state = 42) keeps 114 patients "
        "unseen during training. A 300-tree Random Forest is trained and compared with a standardised Logistic "
        "Regression baseline. Each prediction is explained in two complementary ways. LIME fits a proximity-weighted "
        "linear surrogate to 5,000 seeded perturbations around the patient. TreeSHAP computes exact Shapley "
        "attributions in probability units, which drive local waterfall and force plots as well as global feature "
        "importance. A seven-tab Streamlit dashboard presents predictions, explanations, model evaluation, what-if "
        "analysis and case studies. On the held-out set the Random Forest achieved 97.37% accuracy, 100% precision, "
        "92.86% recall, an F1-score of 96.30% and a ROC-AUC of 0.9944 (TN = 72, FP = 0, FN = 3, TP = 39). SHAP "
        "additivity held with a maximum error of 4.4 × 10^{−16}. Across all 114 test patients, LIME and SHAP shared on "
        "average 3.66 of their top-five features (mean Jaccard similarity 0.62, mean Spearman correlation 0.70), and "
        "28.9% of patients showed at least one directional disagreement. Agreement was complete for confident "
        "predictions but collapsed for the two missed malignancies studied in detail (Patients #86 and #73), where "
        "LIME's local fit fell to R² ≤ 0.06. The study shows that explanations must themselves be audited before they "
        "are trusted in clinical decision support.")
    R.p("**Keywords:** Explainable Artificial Intelligence; LIME; SHAP; TreeSHAP; Random Forest; Breast Cancer "
        "Diagnosis; Clinical Decision Support", align=WD_ALIGN_PARAGRAPH.LEFT)

    # ------------------------------------------------------------ TOC, LOF, LOT
    R.prelim_title("Table of Contents")
    R.field_paragraph('TOC \\o "1-3" \\h \\z \\u', "Right-click and choose Update Field to build the table of contents.")
    R.h1("List of Figures")
    R.field_paragraph('TOC \\h \\z \\t "Figure Caption,1"', "Right-click and choose Update Field to build the list of figures.")
    R.h1("List of Tables")
    R.field_paragraph('TOC \\h \\z \\t "Table Caption,1"', "Right-click and choose Update Field to build the list of tables.")

    # ------------------------------------------------------------ abbreviations
    R.h1("List of Abbreviations")
    abbr = [
        ("AI", "Artificial Intelligence"), ("AUC", "Area Under the (ROC) Curve"),
        ("BL", "Bloom's (Taxonomy) Level"), ("CIAP", "Continuous Internal Assessment for Practical"),
        ("CM", "Confusion Matrix"), ("CO", "Course Outcome"), ("CPU", "Central Processing Unit"),
        ("CSV", "Comma-Separated Values"), ("CV", "Cross-Validation"), ("DFD", "Data-Flow Diagram"),
        ("DPDP", "Digital Personal Data Protection (Act, India, 2023)"), ("EU", "European Union"),
        ("FN / FP", "False Negative / False Positive"), ("FNA", "Fine-Needle Aspirate"),
        ("HTML", "HyperText Markup Language"), ("ICMR", "Indian Council of Medical Research"),
        ("IEEE", "Institute of Electrical and Electronics Engineers"),
        ("ISO/IEC", "International Organization for Standardization / International Electrotechnical Commission"),
        ("JSON", "JavaScript Object Notation"), ("LIME", "Local Interpretable Model-agnostic Explanations"),
        ("LR", "Logistic Regression"), ("NBA", "National Board of Accreditation"), ("PNG", "Portable Network Graphics"),
        ("PO / PSO", "Program Outcome / Program-Specific Outcome"), ("R²", "Coefficient of determination"),
        ("RF", "Random Forest"), ("ROC", "Receiver Operating Characteristic"), ("SAR", "Self-Assessment Report"),
        ("SDG", "(UN) Sustainable Development Goal"), ("SHAP", "SHapley Additive exPlanations"),
        ("TN / TP", "True Negative / True Positive"), ("TPR", "True Positive Rate"),
        ("TreeSHAP", "Tree-specific polynomial-time SHAP algorithm"), ("UCI", "University of California, Irvine"),
        ("UI", "User Interface"), ("UN", "United Nations"), ("WHO", "World Health Organization"),
        ("XAI", "Explainable Artificial Intelligence"),
    ]
    R.table("t_abbr", None, ["Abbreviation", "Expansion"], [[a, b] for a, b in abbr], [1.5, 4.5], font_size=10,
            bold_first_col=True)


# ====================================================================== CHAPTER 1
def chapter1(R: Report, D: dict, cite):
    R.h1("Chapter 1: Problem Definition & Operational Relevance", chapter="1")
    R.h2("1.1 Problem Statement and Background")
    R.p(f"Breast cancer is the most commonly diagnosed cancer in women worldwide. The World Health Organization "
        f"reports about 2.3 million new diagnoses and 670,000 deaths in 2022 {cite('who2024bc')}. A common "
        f"diagnostic step is the fine-needle aspirate (FNA): a thin needle draws cells from a breast mass, and a "
        f"cytologist judges whether the cells look benign or malignant. In the early 1990s Street, Wolberg and "
        f"Mangasarian showed that this judgement can be supported by computer vision. They digitised FNA slides, "
        f"traced the outline of each cell nucleus, and summarised ten shape and texture measurements per sample "
        f"{cite('street1993')}. The resulting Breast Cancer Wisconsin (Diagnostic) dataset {cite('uci1995')} is the "
        f"data used in this project.")
    R.p("Modern classifiers reach high accuracy on such data, but the most accurate ones, such as tree ensembles "
        "and neural networks, are opaque. A Random Forest with 300 trees contains thousands of decision nodes "
        f"(10,976 in the model built here) {cite('breiman2001')}. No clinician can trace by hand how a particular "
        "patient's measurements led to a *malignant* or *benign* output. This is the **black-box problem** in clinical "
        "decision support. A prediction that cannot be explained cannot be checked, challenged or responsibly "
        f"acted upon {cite('rudin2019', 'holzinger2017')}.")
    R.p("Post-hoc explanation methods try to close this gap without giving up accuracy. Two of the most widely "
        f"used are LIME {cite('ribeiro2016')}, which approximates the model locally with a simple linear surrogate, and "
        f"SHAP {cite('lundberg2017')}, which assigns each feature a game-theoretic share of the prediction. In practice "
        "they are often used as if they were interchangeable sources of truth, yet they can disagree with each other "
        f"{cite('krishna2022')}.")
    R.p("**Problem statement.** Given the 30 nuclear measurements of a patient's FNA sample, ClinXAI must (i) predict "
        "the probability that the tumour is malignant with a complex tree ensemble, (ii) explain that individual "
        "prediction with both LIME and SHAP for the same target class, (iii) summarise the model's global behaviour, "
        "and (iv) measure where and why the two explanation methods disagree, especially on clinically risky edge "
        "cases.")

    R.h2("1.2 Clinical and Societal Relevance")
    R.p("The operational failure this project targets is not a wrong prediction alone. It is a wrong prediction "
        "that *looks* well-justified. Three concrete failure modes motivate the work:")
    R.bullets([
        "**Unexplained output.** A probability score with no reasons invites either blind trust (automation bias) or "
        "blanket rejection. Neither supports safe care.",
        "**A false negative hidden behind a confident explanation.** A missed malignancy delays treatment. If the "
        "attached explanation looks plausible, the error is harder to catch. Chapter 5 shows that the explanations "
        "are least consistent on exactly these patients.",
        "**Single-explainer reliance.** Teams usually adopt one explanation method. When two well-founded methods give "
        f"different reasons for the same prediction, at least one of them misrepresents the model {cite('krishna2022')}. "
        "That disagreement is invisible unless it is measured.",
    ])
    R.p("Standard practice falls short in two ways. Intrinsically interpretable models such as logistic regression are "
        "transparent but constrain the model's form. Opaque models paired with a single unaudited explanation offer "
        "accuracy but only an illusion of transparency. Regulators increasingly require transparency and human "
        "oversight for high-risk AI. The EU Artificial Intelligence Act treats AI that acts as a safety component of "
        f"medical devices as high-risk {cite('euaiact2024')}, and the WHO's guidance on AI for health lists "
        f"transparency, explainability and intelligibility among its core principles {cite('who2021')}. Without "
        "auditable explanations, such tools are hard to justify ethically, legally or clinically.")

    R.h2("1.3 Project Objectives")
    R.p("The project pursued four measurable engineering objectives:")
    R.table("t_obj", "Project objectives and their measurable success criteria",
            ["No.", "Objective (Bloom's action verb)", "Measurable criterion"],
            [["O1", "**Implement and evaluate** a Random Forest diagnostic classifier with malignant as the positive "
                    "class, and compare it with an interpretable Logistic Regression baseline.",
              "Accuracy, precision, recall, F1, ROC-AUC and confusion matrix reported on 114 held-out patients; no "
              "test data used for training."],
             ["O2", "**Apply** LIME and TreeSHAP to explain individual predictions of the malignant-class probability, "
                    "and **construct** global SHAP importance.",
              "Local explanations for every test patient; SHAP additivity verified to an error below 10^{−6}."],
             ["O3", "**Quantify and analyse** agreement between LIME and SHAP explanations.",
              "Top-5 overlap, Jaccard similarity, Spearman rank correlation, direction agreement and LIME seed "
              "stability for all 114 patients and five programmatically selected case studies."],
             ["O4", "**Design and validate** an interactive dashboard that presents predictions and explanations "
                    "transparently.",
              "Seven-tab Streamlit application verified by automated tests and a real-browser click-through."]],
            [0.45, 2.85, 2.7], align=["c", "l", "l"])

    R.h2("1.4 Project Scope and Operational Boundaries")
    R.p("**In scope.** Binary malignant/benign prediction from the 30 tabular features. Random Forest and Logistic "
        "Regression models. LIME (tabular) and SHAP (TreeExplainer) explanations of P(malignant). Quantitative "
        "LIME–SHAP comparison. Five reproducible case studies. A local Streamlit dashboard. Automated tests and "
        "report-ready evidence files.")
    R.p("**Out of scope.** The system does not accept raw microscope images, so it is not an image classifier. It "
        "makes no calibrated risk estimates and gives no treatment recommendations. It has no clinical or external "
        "validation, no fairness audit (the dataset has no demographic attributes), no adversarial or privacy "
        "attacks, and no public deployment.")
    R.p("**Interpretation of the title.** The word *multi-modal* refers to the two complementary explanation "
        "modalities, a local surrogate (LIME) and game-theoretic attribution (SHAP), presented in both visual and "
        "tabular form. The input data is a single tabular modality, although it is derived from images. Genuine image "
        "plus tabular fusion is identified as future work (Section 7.4).")
    R.p("**Assumptions and constraints.** The dataset labels are taken as ground truth. Features are assumed to be "
        "measured the same way as in the original study. All computation runs on a CPU-only Windows 11 PC with Python "
        "3.12, with no GPU, internet service or external API. The dataset is small (569 patients), so the test set "
        "has only 114 patients, and every metric carries sampling uncertainty.")


# ====================================================================== CHAPTER 2
def chapter2(R: Report, D: dict, cite):
    F = D["facts"]
    R.h1("Chapter 2: Theoretical Formulation, Literature Review & Mathematical Framework", chapter="2")
    R.h2("2.1 Explainable Artificial Intelligence")
    R.p(f"Explainable AI (XAI) studies methods that make a model's behaviour understandable to humans "
        f"{cite('adadi2018', 'arrieta2020')}. Doshi-Velez and Kim define interpretability as the ability to explain or "
        f"present a model's reasoning in understandable terms to a human {cite('doshivelez2017')}. Lipton cautions "
        f"that the word covers several different properties that should be stated explicitly {cite('lipton2018')}. "
        "Three distinctions organise the field:")
    R.bullets([
        "**Intrinsic vs post-hoc.** Some models are interpretable by construction, such as sparse linear models or "
        "short decision trees. Others are explained after training by a separate method, as LIME and SHAP do.",
        "**Local vs global.** A local explanation justifies one prediction for one patient. A global explanation "
        "describes the model's behaviour over a population.",
        "**Model-agnostic vs model-specific.** Model-agnostic methods only query predictions, as LIME does. "
        "Model-specific methods exploit internal structure, as TreeSHAP does with tree paths.",
    ])
    R.p("Explanations are judged against several desiderata. This report uses five of them precisely. **Local "
        "fidelity** is how closely an explanation reproduces the model near the instance. **Consistency** means that "
        "if a model relies more on a feature, its attribution should not decrease. **Stability** means that repeated "
        "or slightly perturbed explanations stay similar. **Comprehensibility** concerns how easily a human can read "
        "the explanation. **Computational cost** is the time needed to produce it. Rudin argues that for high-stakes "
        f"decisions an interpretable model is preferable to an explained black box {cite('rudin2019')}. ClinXAI "
        "tests that trade-off directly with its Logistic Regression baseline.")

    R.h2("2.2 Random Forest Classification")
    R.p(f"A Random Forest {cite('breiman2001')} is an ensemble of T decision trees. Each tree is grown on a bootstrap "
        "sample of the training set, and each split considers only a random subset of features. In this project "
        f"T = 300, splits use the Gini criterion, max_features = \"sqrt\" (⌊√30⌋ = 5 candidate features per split), "
        "and trees are grown until their leaves are pure (max_depth = None, min_samples_leaf = 1). Scikit-learn "
        f"{cite('pedregosa2011')} averages the class-probability estimates of the trees:")
    R.eq("f(x) = P̂(y = 1 | x) = (1/T) · Σ_{t=1..T} p_{t}(y = 1 | x)", "(2.1)")
    R.p("Here p_{t}(y = 1 | x) is the fraction of malignant training samples in the leaf of tree t that x reaches. "
        "Because the leaves are almost always pure, this is close to the fraction of trees voting malignant. The "
        "predicted class is malignant when f(x) ≥ 0.5. Each split is chosen to minimise the weighted Gini impurity "
        "of the child nodes:")
    R.eq("G(node) = 1 − Σ_{k ∈ {0,1}} p_{k}^{2}", "(2.2)")
    R.p("where p_{k} is the proportion of class k in the node. Averaging many de-correlated trees reduces variance and "
        f"gives strong accuracy. The price is opacity: the trained forest has {F['rf_structure']['total_nodes']:,} "
        f"nodes and {F['rf_structure']['total_leaves']:,} leaves, with a mean tree depth of "
        f"{F['rf_structure']['mean_depth']} and a maximum depth of {F['rf_structure']['max_depth']}. The baseline, "
        "Logistic Regression, models P(y = 1 | x) = σ(wᵀx̃ + b), where x̃ is the standardised feature vector and "
        "σ(u) = 1/(1 + e^{−u}). Its coefficients can be read directly.")

    R.h2("2.3 LIME: Local Interpretable Model-Agnostic Explanations")
    R.p(f"LIME {cite('ribeiro2016')} explains a single prediction f(x) by learning a simple, interpretable model g "
        "that imitates f only in the neighbourhood of x. It is model-agnostic: it needs only the ability to call "
        "`predict_proba` on new inputs. For tabular data, the LIME library used here (version 0.2.0.1) "
        f"{cite('limerepo')} works in three stages. It maps each continuous feature to an interpretable "
        "representation by discretising it into quartile bins learnt from the training data. It generates "
        "perturbed samples around the patient and queries the black-box model on them. It then fits a weighted linear "
        "model whose coefficients become the explanation, for example \"`worst area > 1122.50` adds +0.137 to "
        "P(malignant)\".")

    R.h2("2.4 LIME Perturbation and Local Surrogate Formulation")
    R.p("LIME selects the explanation g from a class G of interpretable models (here, linear models) by solving")
    R.eq("ξ(x) = argmin_{g ∈ G}  L(f, g, π_{x}) + Ω(g)", "(2.3)")
    R.p("where f is the black-box model (the Random Forest's P(malignant)). L measures how unfaithful g is to f in "
        "the neighbourhood of x. π_{x} is a proximity kernel that defines that neighbourhood. Ω(g) penalises the "
        "complexity of g. The fidelity term is a proximity-weighted squared loss over N perturbed samples z_{i} with "
        "interpretable representations z′_{i}:")
    R.eq("L(f, g, π_{x}) = Σ_{i=1..N} π_{x}(z_{i}) · ( f(z_{i}) − g(z′_{i}) )^{2}", "(2.4)")
    R.eq("π_{x}(z) = exp( − D(x, z)^{2} / (2σ^{2}) ),     σ = 0.75 · √d", "(2.5)")
    R.p(f"Here D is the Euclidean distance in LIME's standardised representation and d = 30 is the number of "
        f"features, so σ = 0.75·√30 ≈ {F['kernel_width_default']}. The library implements the kernel as "
        "√(exp(−D²/σ²)), which is algebraically identical to Equation (2.5). With quartile discretisation, "
        "z′_{j} ∈ {0, 1} indicates whether perturbed sample z falls in the *same* quartile bin as the patient for "
        "feature j. The surrogate is linear in these indicators:")
    R.eq("g(z′) = w_{0} + Σ_{j=1..d} w_{j} · z′_{j},     Ω(g) = λ · ‖w‖^{2}  (ridge, λ = 1)", "(2.6)")
    R.p("Each coefficient w_{j} is the explanation weight for feature j's condition. A positive value pushes the "
        "surrogate toward malignant, and a negative value pushes it toward benign. LIME also reports the weighted "
        "coefficient of determination R² of the surrogate on its own samples. **R² is the only built-in fidelity "
        "signal**: a low R² means the linear surrogate does not reproduce the forest's behaviour near this patient. "
        "Because the N samples are random, the explanation depends on the random seed and on N. This sensitivity to "
        f"perturbations is a documented weakness {cite('alvarez2018')}. ClinXAI fixes the seed (42) and N (5,000) for "
        "reproducibility and measures stability separately (Section 5.9).")

    R.h2("2.5 SHAP: Shapley Additive Explanations")
    R.p(f"SHAP {cite('lundberg2017')} unifies several attribution methods under the class of **additive feature "
        "attribution** explanations. Each one expresses the explanation as a linear function of simplified binary "
        "inputs z′ ∈ {0,1}^{M}, where z′_{j} = 1 means feature j is present:")
    R.eq("g(z′) = φ_{0} + Σ_{j=1..M} φ_{j} · z′_{j}", "(2.7)")
    R.p("Lundberg and Lee proved that only one choice of attributions φ_{j} satisfies three desirable properties "
        "together, and that choice is the Shapley value from cooperative game theory:")
    R.bullets([
        "**Local accuracy (additivity).** The attributions sum exactly to the prediction, f(x) = φ_{0} + Σ_{j} φ_{j}, "
        "where the base value φ_{0} = E[f(X)].",
        "**Missingness.** A feature that is absent receives zero attribution.",
        "**Consistency.** If a model changes so that a feature's marginal contribution never decreases, its "
        "attribution never decreases.",
    ])
    R.p("For a classifier explained in probability units, Equation (2.7) gives the identity checked in this project:")
    R.eq("P(malignant | x) = φ_{0} + Σ_{j=1..30} φ_{j}(x)", "(2.8)")

    R.h2("2.6 Shapley Game-Theoretic Attribution")
    R.p(f"Shapley {cite('shapley1953')} asked how to divide the payout of a cooperative game fairly among players. In "
        "SHAP, the players are the M features, a coalition S ⊆ F is a subset of features whose values are known, and "
        "the payout of a coalition is the model's expected output given only those features, v_{x}(S) = "
        "E[f(X) | X_{S} = x_{S}]. Feature j's Shapley value averages its marginal contribution over all orderings in "
        "which features can join the coalition:")
    R.eq("φ_{j}(x) = Σ_{S⊆F∖{j}} [|S|!·(M−|S|−1)!/M!]·[v_{x}(S∪{j}) − v_{x}(S)]", "(2.9)")
    R.p("The Shapley value is the unique attribution satisfying the axioms of **efficiency** (attributions sum to "
        "v_{x}(F) − v_{x}(∅)), **symmetry** (interchangeable features receive equal credit), **dummy** (a feature "
        "that never changes the payout receives zero), and **additivity** (attributions for a sum of games are the "
        "sums of the attributions). Evaluated exactly, Equation (2.9) needs 2^{M} coalitions per patient. For "
        "M = 30 that is 2^{30} ≈ 1.07 × 10^{9} coalitions, which is impractical without a model-specific algorithm.")

    R.h2("2.7 TreeSHAP Explanation Method")
    R.p(f"TreeSHAP {cite('lundberg2020')} computes Equation (2.9) **exactly and in polynomial time** for tree models. "
        "It pushes all coalitions through each tree simultaneously, tracking the proportion of training samples "
        "(the *cover*) that follow each branch. Its cost is O(T · L · D^{2}) per explained sample, where T is the "
        "number of trees, L the maximum number of leaves and D the maximum depth. ClinXAI uses the default "
        "*tree-path-dependent* variant (`shap.TreeExplainer(model)`). It needs no background dataset, because it "
        "estimates the conditional expectation v_{x}(S) from the training-sample cover stored in each node.")
    R.p("Two properties make TreeSHAP especially suitable here. First, Shapley values are linear in the model, so the "
        "forest's attribution is the average of the per-tree attributions, φ_{j}(RF) = (1/T) Σ_{t} φ_{j}(tree_{t}). "
        "Second, a scikit-learn classification tree's raw output is a class-probability fraction. The SHAP values, "
        "the base value and `predict_proba` therefore share **probability units**, and Equation (2.8) can be "
        "verified numerically (Section 5.7). The base value is the forest's expected output over its bootstrap "
        f"training samples, 0.3747. That is close to the training prevalence of malignancy, "
        f"{F['train_malignant']}/455 = 0.374. The path-dependent variant reflects the *model's* learned structure. It "
        "is not a causal statement about tumour biology, and with strongly correlated features it can spread credit "
        "in ways that differ from interventional variants that use a background dataset.")

    R.h2("2.8 LIME versus SHAP: Mathematical and Practical Trade-offs")
    R.p("Both methods produce a signed weight per feature for the same patient and the same target class. The weights "
        "answer different questions, so they **cannot be compared in magnitude**. A LIME weight is the effect of a "
        "binary *bin indicator* in a weighted linear surrogate over a sampled neighbourhood. A SHAP value is an exact "
        "share of the prediction relative to the base value. @[t_lime_vs_shap_theory] summarises the practical differences.")
    R.table("t_lime_vs_shap_theory", "Theoretical and practical comparison of LIME and TreeSHAP as used in ClinXAI",
            ["Property", "LIME (tabular)", "TreeSHAP (path-dependent)"],
            [["Model access", "Model-agnostic: calls predict_proba only", "Model-specific: reads tree structure"],
             ["Explanation unit", "Weight of a quartile-bin indicator in a ridge surrogate",
              "Additive share of P(malignant) relative to base value φ_{0}"],
             ["Local fidelity", "Approximate; measured by surrogate R² (mean 0.27 in this project)",
              "Exact: φ_{0} + Σφ_{j} = f(x) (error 4.4 × 10^{−16})"],
             ["Consistency guarantee", "None", "Yes (Shapley axioms)"],
             ["Stability", "Varies with random seed and sample count", "Deterministic for a fixed model"],
             ["Baseline / reference", "Other bins under the training distribution", "E[f(X)] over training cover"],
             ["Handling of correlation", "Perturbs features independently (can create unrealistic samples)",
              "Conditional expectation along tree paths"],
             ["Cost per patient (here)", "5,000 model calls + ridge fit (≈ 0.2–0.3 s)",
              "Polynomial and exact; all 114 test patients are explained once at dashboard start-up (total "
              "start-up 6–8 s)"],
             ["Global view", "Not native", "Mean |φ_{j}| importance, beeswarm"]],
            [1.5, 2.25, 2.25], keep_together=False)
    R.p("ClinXAI quantifies agreement with three measures, computed only for the same patient and the same class. Let "
        "A and B be the sets of top-k features ranked by |weight| for LIME and |φ| for SHAP, with k = 5:")
    R.eq("J(A, B) = |A ∩ B| / |A ∪ B|", "(2.10)")
    R.eq("ρ = 1 − 6 · Σ_{j} d_{j}^{2} / ( n · (n^{2} − 1) )", "(2.11)")
    R.p("J is the Jaccard similarity: 1 means identical top-5 sets and 0 means no shared feature. ρ is Spearman's "
        "rank correlation between the |LIME| and |SHAP| rankings over all n = 30 features, where d_{j} is the rank "
        "difference of feature j (written here in its no-ties form). **Direction disagreement** counts features in "
        "A ∪ B whose LIME weight and SHAP value have opposite signs. These are measures of agreement *between "
        "explanation methods*. They are not clinical validation metrics.")

    R.h2("2.9 Comparative Literature Review")
    R.p("@[t_lit] places the methods used in ClinXAI among related, well-established approaches to explaining "
        "tabular classifiers.")
    R.table("t_lit", "Comparative summary of explanation approaches relevant to ClinXAI",
            ["Approach", "Type / scope", "Key strength", "Computational cost", "Main limitation"],
            [[f"Logistic regression coefficients {cite('rudin2019')}", "Intrinsic, global + local",
              "Directly readable; faithful by construction", "Very low", "Restricted (linear) model form"],
             [f"Permutation importance {cite('breiman2001')}", "Post-hoc, global", "Simple, model-agnostic",
              "Moderate (re-scoring)", "No per-patient explanation; affected by correlation"],
             [f"LIME {cite('ribeiro2016')}", "Post-hoc, local, agnostic", "Works for any model; intuitive rules",
              "Moderate (N model calls)", "Sampling instability; no fidelity guarantee"],
             [f"Anchors {cite('ribeiro2018')}", "Post-hoc, local rules", "High-precision if-then rules",
              "High (search)", "Coverage may be small"],
             [f"KernelSHAP {cite('lundberg2017')}", "Post-hoc, local, agnostic", "Shapley properties for any model",
              "High (sampling coalitions)", "Approximate; needs a background set"],
             [f"TreeSHAP {cite('lundberg2020')}", "Post-hoc, local + global, tree-specific",
              "Exact, fast, consistent", "Low (polynomial)", "Trees only; path-dependent assumptions"]],
            [1.35, 1.15, 1.3, 1.0, 1.2], font_size=9, keep_together=False)
    R.p(f"Research on the reliability of these methods motivates ClinXAI's comparison. Alvarez-Melis and Jaakkola "
        f"found that LIME and related methods can change markedly under small input perturbations "
        f"{cite('alvarez2018')}. Slack et al. showed that because LIME and KernelSHAP rely on perturbed, often "
        f"off-distribution samples, a model can be built to hide its true behaviour from them {cite('slack2020')}. "
        f"Krishna et al. documented the *disagreement problem*: practitioners regularly see explanation methods "
        f"disagree on top features and signs, and they have no principled way to resolve it {cite('krishna2022')}. "
        f"In the medical domain, Holzinger et al. argue that explainability is a prerequisite for clinical acceptance "
        f"{cite('holzinger2017')}. Molnar's text gives an accessible overview of these methods "
        f"{cite('molnar2022')}. ClinXAI contributes a small, fully reproducible case study of this disagreement on a "
        "clinical benchmark. It shows *where* disagreement occurs (Chapter 5) and links it to model uncertainty and "
        "missed malignancies.")
