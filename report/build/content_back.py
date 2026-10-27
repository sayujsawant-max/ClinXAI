"""Chapter 6, Chapter 7, References and Appendices A–B."""
import json
from pathlib import Path

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

from engine import Report, add_marked_runs
from refs import REFS

PROJ = Path(__file__).resolve().parents[2]


# ====================================================================== CHAPTER 6
def chapter6(R: Report, D: dict, cite):
    rf = D["metrics"]["random_forest"]
    R.h1("Chapter 6: Societal Impact, Ethical Governance, Safety & Security Audits", chapter="6")
    R.h2("6.1 Importance of Transparency in Clinical AI")
    R.p(f"In clinical decision support, transparency is a safety mechanism, not a courtesy. Explanations let a "
        f"clinician check a prediction against their own knowledge, notice when a model relies on an implausible "
        f"signal, and explain a decision to the patient {cite('holzinger2017')}. The WHO lists ensuring transparency, "
        f"explainability and intelligibility among its six principles for AI in health {cite('who2021')}. ClinXAI "
        "adds a second lesson from Chapter 5: transparency must cover the *explanations themselves*. The dashboard "
        "therefore shows LIME and SHAP side by side for the same patient and class, reports LIME's own fidelity (R²) "
        "and stability, and flags sign conflicts, so that disagreement is visible instead of hidden.")

    R.h2("6.2 Human Oversight and Clinical Decision Support")
    R.p("ClinXAI is designed as a **decision-support aid for education**, never as an autonomous diagnostic system. "
        "Its human-oversight features are:")
    R.bullets([
        "A persistent disclaimer on every view: research and educational demonstration only, not a medical device, no "
        "diagnosis or treatment decisions.",
        "The probability is labelled as an uncalibrated model score, so it is not read as a clinical risk.",
        "A borderline warning when |P − 0.5| < 0.15, and an extrapolation warning when inputs leave the training range.",
        "Explanation-quality indicators: a low-R² warning for LIME, the stability toggle and the direction-disagreement "
        "count.",
        "No recommendation is ever generated. The output is a score plus explanations for a human to evaluate.",
    ])
    R.p("A responsible clinical workflow built on this design would keep the clinician as the decision-maker. It "
        "would route any prediction that is borderline, out of range, or shows LIME–SHAP disagreement to mandatory "
        "human review, and it would record the final human decision separately from the model output.")

    R.h2("6.3 Patient Privacy and Responsible Data Usage")
    R.p(f"The project uses only the public, de-identified Breast Cancer Wisconsin (Diagnostic) dataset {cite('uci1995')}. "
        "It contains no names, identifiers or demographic attributes. ClinXAI collects no user data, makes no network "
        "calls to external AI services, and keeps all computation and files on the local machine. Under India's "
        f"Digital Personal Data Protection Act, 2023 {cite('dpdp2023')}, processing identifiable patient data in a "
        "future clinical version would require, among other obligations, a lawful basis such as informed consent, "
        "purpose limitation and reasonable security safeguards. None of these is needed for, or claimed by, the "
        "present educational prototype.")

    R.h2("6.4 Model Bias, Dataset Limitations and Generalisation")
    R.bullets([
        "**Single-centre, historical data.** All 569 samples come from one institution's FNA imaging pipeline in the "
        "early 1990s. The data cannot represent other populations, scanners, staining protocols or sample-preparation "
        "practices.",
        "**No demographic attributes.** Age, ethnicity and similar variables are absent, so subgroup performance and "
        "fairness *cannot be audited* with this data. The project does not claim to be fair across groups.",
        "**Class imbalance.** With 37% malignant cases, accuracy alone would flatter the model. This is why recall, "
        "precision, F1 and AUC are reported.",
        "**Distribution shift.** Features measured on new equipment could shift systematically. The model would then "
        "extrapolate, which the dashboard warns about only for values outside the training range, not for subtler "
        "shifts within it.",
        "**Small test set.** 114 patients, including 42 malignant, give wide uncertainty on every metric.",
    ])

    R.h2("6.5 Safety Considerations and False Negatives")
    R.p(f"The model's only errors on the test set were **{rf['confusion_matrix']['fn']} false negatives**: malignant "
        "tumours predicted benign (Patients #73, #86 and #385). In screening and diagnosis a false negative can delay "
        "treatment, so it is the most harmful error type. Section 5.9 showed that these patients also receive the "
        "least faithful and least consistent explanations. A clinician therefore could not rely on the explanation to "
        "catch the error. @[t_audit] audits the system's main failure modes and robustness issues honestly, including "
        "those that were not mitigated.")
    R.table("t_audit", "Safety, robustness and security audit of the prototype",
            ["Failure mode / threat", "Evidence in this project", "Mitigation present", "Residual risk / not done"],
            [["Missed malignancy (FN)", "3 FNs; P = 0.160–0.297", "Borderline warning; disagreement signals",
              "Threshold not tuned; no calibration"],
             ["Unfaithful local explanation", "Mean LIME R² 0.27; ≤ 0.06 on FNs", "R² shown; warning if < 0.3",
              "No automatic suppression of weak explanations"],
             ["Explanation instability", "LIME seed Jaccard as low as 0.00 (#86)", "Fixed seed; stability toggle",
              "More samples or averaging not implemented"],
             ["Invalid / corrupted input", "NaN, ∞, text, negatives, missing fields", "validate_patient_input (tested)",
              "—"],
             ["Out-of-distribution input", "Value above training maximum", "Extrapolation warning (browser-verified)",
              "No detection of in-range shift"],
             [f"Adversarial explanation manipulation {cite('slack2020')}", "Not tested", "None",
              "Possible for perturbation-based explainers"],
             ["Tampered model file", "joblib uses Python pickle", "Bundle loaded only from the local project folder",
              "No checksum or signature verification"],
             ["Unauthorised access", "Local single-user app", "Runs on localhost only", "No authentication or audit log"]],
            [1.45, 1.55, 1.55, 1.45], font_size=9, keep_together=False)
    R.p("The pickle point deserves emphasis. Loading a joblib file executes code during unpickling, so a replaced "
        "`models/clinxai_rf_bundle.joblib` could run arbitrary code. In this prototype the file is created and read "
        "locally by the same user. A deployed version should verify a cryptographic hash before loading, or use a "
        "non-executable model format.")

    R.h2("6.6 Relevant Ethical and Regulatory Considerations")
    R.p("ClinXAI is an educational prototype that is not placed on any market and is not used clinically. It is "
        "therefore **not claimed to comply with, be certified under, or be clinically validated against** any of "
        "the frameworks below. @[t_reg] maps their relevant principles to what the prototype demonstrates, to show "
        "the gap a real clinical product would have to close.")
    R.table("t_reg", "Illustrative alignment with ethical and regulatory frameworks (not a compliance claim)",
            ["Framework", "Relevant principle", "What ClinXAI demonstrates", "Gap for real clinical use"],
            [[f"EU AI Act, Reg. (EU) 2024/1689 {cite('euaiact2024')}",
              "Medical-device AI is high-risk; transparency to deployers (Art. 13), human oversight (Art. 14), "
              "accuracy and robustness (Art. 15)",
              "Explanations, disclaimers, warnings, reported accuracy and robustness limits",
              "Risk-management system, technical documentation, conformity assessment, post-market monitoring"],
             [f"WHO guidance, 2021 {cite('who2021')}",
              "Autonomy; safety; transparency and explainability; accountability; inclusiveness; sustainability",
              "Human decision retained; transparent outputs; limits stated", "Clinical evaluation; equity assessment"],
             [f"ICMR AI ethics guidelines, 2023 {cite('icmr2023')}",
              "Principles including autonomy, data quality, equity, non-discrimination and validity (clinical and "
              "field validation before use)",
              "Public de-identified data; documented validation of software behaviour",
              "Ethics-committee approval; clinical and field validation"],
             [f"DPDP Act, 2023 {cite('dpdp2023')}", "Lawful, consented, purpose-limited processing of personal data",
              "No personal data processed", "Consent, notices, security safeguards for real patient data"],
             [f"ISO/IEC 23894:2023 {cite('iso23894')}", "AI risk identification, analysis and treatment",
              "Informal risk audit (@[t_audit])", "Formal, documented risk-management process"],
             [f"IEEE Ethically Aligned Design {cite('ieee2019ead')}", "Transparency, accountability, awareness of misuse",
              "Open methods, reproducible evidence, misuse warnings", "Independent review"]],
            [1.3, 1.6, 1.55, 1.55], font_size=8.5, keep_together=False)

    R.h2("6.7 Alignment with UN Sustainable Development Goal 3")
    R.p(f"SDG 3, *Good Health and Well-being* {cite('un2015')}, includes target 3.4: by 2030, reduce premature "
        "mortality from non-communicable diseases, such as cancer, by one third through prevention and treatment. "
        "Trustworthy diagnostic support could contribute to earlier and more consistent detection, particularly where "
        "specialist cytologists are scarce. ClinXAI's contribution is methodological. It shows how to make a "
        "diagnostic model's reasoning inspectable, and it warns that explanation methods themselves can mislead on the "
        "hardest cases. The prototype is also light on resources: training takes about 7 seconds and the full "
        "evaluation about 36 seconds on a CPU, with no GPU, so the approach is reproducible in low-resource teaching "
        "settings. Any real health impact would depend on clinical validation, which has not been done.")


# ====================================================================== CHAPTER 7
def chapter7(R: Report, D: dict, cite):
    rf = D["metrics"]["random_forest"]
    agg = D["cases"]["aggregate_test_set"]
    R.h1("Chapter 7: Conclusion, Engineering Limitations & Future Enhancements", chapter="7")
    R.h2("7.1 Summary of Work Completed")
    R.p("ClinXAI delivers a complete, reproducible explainable-diagnostics pipeline for the Breast Cancer Wisconsin "
        "(Diagnostic) dataset. A 300-tree Random Forest predicts the probability of malignancy. LIME and TreeSHAP "
        "explain every prediction for the same malignant class, and SHAP also provides global importance. A dedicated "
        "comparison module quantifies where the explainers agree. A seven-tab Streamlit dashboard makes all of this "
        "interactive, including what-if analysis and five programmatically selected case studies. The system is "
        "covered by 24 automated tests, an independent validation of every saved output, and a real-browser "
        "click-through. All report figures and tables are generated from the actual implementation.")

    R.h2("7.2 Achievement of Project Objectives")
    R.table("t_achieve", "Achievement of the project objectives defined in Section 1.3",
            ["Objective", "Status", "Evidence"],
            [["O1 — Random Forest classifier and baseline", "Achieved",
              f"Accuracy {100 * rf['accuracy']:.2f}%, precision {100 * rf['precision']:.0f}%, recall "
              f"{100 * rf['recall_sensitivity']:.2f}%, F1 {100 * rf['f1']:.2f}%, ROC-AUC {rf['roc_auc']:.4f}; "
              "LR baseline on the same split (@[t_metrics])"],
             ["O2 — LIME and TreeSHAP explanations", "Achieved",
              "Local explanations for all 114 test patients; global bar and beeswarm; SHAP additivity error 4.4 × 10^{−16}"],
             ["O3 — Quantified LIME–SHAP agreement", "Achieved",
              f"Mean overlap {agg['mean_top5_overlap']:.2f}/5, Jaccard {agg['mean_top5_jaccard']:.2f}, Spearman "
              f"{agg['mean_spearman_abs']:.2f}, direction disagreement in {agg['pct_patients_with_direction_disagreement']:.1f}% "
              "of patients; 5 case studies; stability analysis"],
             ["O4 — Interactive, validated dashboard", "Achieved (local)",
              "Seven tabs; 24/24 tests; 34/34 browser checks; runs locally, not publicly deployed"]],
            [1.9, 0.9, 3.2], font_size=9)
    R.p("The most important finding is not the model's accuracy, which is high and comparable to a linear baseline. "
        "It is that the two most popular post-hoc explanation methods agree on confident predictions and diverge on "
        "uncertain ones and on missed cancers. For Patients #86 and #73, LIME's surrogate explained almost none of the "
        "forest's local behaviour (R² 0.03 and 0.06), and its top features overlapped with SHAP's by zero and one "
        "feature respectively. Explanation disagreement is therefore a practical warning signal for human review.")

    R.h2("7.3 Technical Limitations")
    R.bullets([
        "**Local explanation instability.** LIME's top-5 set changes with the random seed (mean pairwise Jaccard 0.39 "
        "for Patient #86, with one pair fully disjoint). The fixed seed gives reproducibility but not robustness.",
        "**Low LIME fidelity.** The mean surrogate R² is 0.27 and falls to about 0.03–0.06 on the false negatives. "
        "Quartile discretisation and two-decimal rule display (for example `0.00 < fractal dimension error <= 0.00`) "
        "further reduce readability.",
        "**SHAP computation and background assumptions.** The path-dependent TreeSHAP variant uses the trees' "
        "training cover instead of an explicit background dataset. Interventional SHAP with a chosen background, or "
        "KernelSHAP, could distribute credit among the highly correlated features differently. Those variants were "
        "not evaluated.",
        "**Small dataset.** With 569 patients and a single 114-patient test split, every metric has wide sampling "
        "uncertainty. Only 3 false negatives exist to study.",
        "**Possible distribution shift.** The data comes from one historical source. Performance and explanations may "
        "not transfer to other populations or imaging pipelines, and in-range shifts are not detected.",
        "**No external clinical validation.** No clinician evaluated the explanations, and the model has not been "
        "tested on external data. Probabilities are uncalibrated.",
        "**Tabular only.** The system uses features derived from images. It does not process images or any second "
        "clinical data modality.",
        "**Engineering limits.** The app is single-user and local, without authentication. The first launch takes "
        "about 6–8 s. Browser verification covered Microsoft Edge at desktop width only.",
    ])

    R.h2("7.4 Future Enhancements")
    R.bullets([
        "**Genuine multimodal diagnostics.** Combine a convolutional network on the raw cytology images with the "
        "tabular nuclear features. Explain the image branch with saliency methods and the tabular branch with SHAP, "
        "then compare the explanations across modalities.",
        "**Explanation quality controls.** Suppress or flag LIME explanations below a fidelity threshold, average LIME "
        "over several seeds or larger samples, and group correlated features before attribution.",
        "**Alternative SHAP formulations.** Compare path-dependent TreeSHAP with interventional TreeSHAP and KernelSHAP "
        "using an explicit background dataset.",
        f"**Calibration and threshold selection.** Calibrate probabilities {cite('niculescu2005')} and choose a "
        "recall-oriented threshold on separate validation data, reporting the false-positive cost.",
        "**External validation and distribution-shift monitoring** on independent datasets.",
        "**Medical expert validation before any deployment.** Run a structured study with pathologists and "
        "oncologists to test whether the explanations are understandable, correct and useful. Without this, the system "
        "must remain an educational tool.",
        "**Deployment hardening.** Add model-file integrity checks, authentication, audit logging and a documented "
        "risk-management process.",
    ])


# ====================================================================== REFERENCES
def references(R: Report, cite):
    R.h1("References", chapter="R")
    for i, key in enumerate(cite.order, start=1):
        para = R.doc.add_paragraph(style="Normal")
        para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pf = para.paragraph_format
        pf.left_indent = Inches(0.45)
        pf.first_line_indent = Inches(-0.45)
        pf.line_spacing = 1.15
        pf.space_after = Pt(6)
        add_marked_runs(para, f"[{i}]\t{REFS[key]}", size=12)
        pf.tab_stops.add_tab_stop(Inches(0.45))


# ====================================================================== APPENDICES
SOURCE_FILES = [
    ("requirements.txt", "Pinned dependencies"),
    (".streamlit/config.toml", "Streamlit theme and server configuration"),
    ("src/__init__.py", "Package marker"),
    ("src/config.py", "Central configuration"),
    ("src/data_loader.py", "Data loading, mapping, validation and split"),
    ("src/model.py", "Model training, evaluation and persistence"),
    ("src/explain_lime.py", "LIME explanations"),
    ("src/explain_shap.py", "SHAP explanations"),
    ("src/comparison.py", "LIME–SHAP comparison and case selection"),
    ("src/visualization.py", "Figures"),
    ("train_model.py", "Training script"),
    ("evaluate.py", "Explanation evaluation script"),
    ("app.py", "Streamlit dashboard"),
    ("tests/test_pipeline.py", "Automated test suite"),
]


def appendix_a(R: Report):
    R.h1("Appendix A: Complete Source Code Listings / Core Configuration Files", chapter="A")
    R.p("This appendix reproduces every source and configuration file of the ClinXAI application exactly as "
        "submitted, read directly from the project folder when the report was generated. Code is set in Consolas "
        "9 pt with single line spacing on a light-grey background. Lines longer than the page width wrap with a "
        "hanging indent.")
    for i, (rel, desc) in enumerate(SOURCE_FILES, start=1):
        lines = (PROJ / rel).read_text(encoding="utf-8").splitlines()
        R.h2(f"A.{i} {rel} — {desc} ({len(lines)} lines)")
        R.code(lines, size=8.5)


def appendix_b(R: Report, D: dict):
    R.h1("Appendix B: Raw Diagnostic Trace Logs, Audit Tables & Verification Sheets", chapter="B")
    R.p("All logs below are unedited console or file outputs from the final build of ClinXAI. Their source files are "
        "kept in `report/evidence/` and `outputs/`.")
    R.h2("B.1 Environment Record")
    R.code(D["environment"].splitlines(), "Python version and package versions (`report/evidence/environment.txt`)")
    R.h2("B.2 Training Console Log")
    R.code(D["train_log"].splitlines(), "`python train_model.py` (`report/evidence/train_model_console.txt`)")
    R.h2("B.3 Evaluation Console Log")
    R.code(D["evaluate_log"].splitlines(), "`python evaluate.py` (`report/evidence/evaluate_console.txt`)")
    R.h2("B.4 Automated Test Log")
    R.code([l for l in D["pytest"].splitlines() if l.strip()], "`python -m pytest -v` (`report/evidence/pytest_verbose.txt`)")
    R.h2("B.5 Independent Output Validation (35 checks)")
    R.code(D["validation"].splitlines(), "Validation of saved outputs (`report/evidence/output_validation.txt`)")
    R.h2("B.6 Real-Browser Verification Sheet (34 checks)")
    R.table("t_browser", "Real-browser click-through results (Playwright + Microsoft Edge)",
            ["No.", "Check", "Result", "Observed detail"],
            [[str(i), r["check"], "PASS" if r["passed"] else "FAIL", r["detail"][:90]]
             for i, r in enumerate(D["browser"], start=1)],
            [0.4, 2.9, 0.55, 2.15], align=["c", "l", "c", "l"], font_size=8)
    R.h2("B.7 SHAP Additivity Record")
    R.code(json.dumps(D["additivity"], indent=2, ensure_ascii=False).splitlines(),
           "`outputs/metrics/shap_additivity.json`")
    R.h2("B.8 Model Metrics Record")
    R.code(json.dumps(D["metrics"], indent=2, ensure_ascii=False).splitlines(), "`outputs/metrics/metrics.json`")
    R.h2("B.9 Case-Study Audit Table")
    rows = []
    for c in D["case_csv"]:
        rows.append([c["case"], c["case_type"], f"#{c['patient_id']}", f"{c['true_label']} / {c['predicted']}",
                     c["p_malignant"], c["top_k_overlap"], c["jaccard_top_k"], c["spearman_abs_all_features"],
                     c["lime_local_r2"], c["lime_stability_mean_jaccard"]])
    R.table("t_case_csv", "Contents of outputs/case_studies/case_studies.csv (numeric columns; direction-disagreement "
            "lists and observations are given in Section 5.8)",
            ["#", "Case", "Patient", "Actual / predicted", "P(mal.)", "Overlap", "Jaccard", "ρ", "LIME R²", "Stability"],
            rows, [0.3, 1.0, 0.6, 1.05, 0.55, 0.55, 0.55, 0.45, 0.5, 0.45],
            align=["c", "l", "c", "l", "c", "c", "c", "c", "c", "c"])
    R.h2("B.10 Descriptive Analysis Record")
    R.code(json.dumps(D["desc"], indent=2).splitlines(),
           "`report/figures/report_descriptive_analysis.json` (computed from test_set_lime_vs_shap.csv by "
           "`report/make_report_figures.py`)")
