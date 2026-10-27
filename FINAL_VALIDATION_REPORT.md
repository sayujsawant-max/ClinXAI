# ClinXAI — Final Validation Report

**Date:** 2026-10-26 · **Environment:** Windows 11, Python 3.12.10, Microsoft Edge (headless, via Playwright 1.64.1)
**Scope:** checks the existing implementation only. No features or architecture changed. Every result below comes
from commands actually executed. Nothing is estimated.

## 1. Verification summary

| Verification layer | Method | Result |
|---|---|---|
| Automated test suite | `python -m pytest -q` (project venv) | **24 / 24 passed** |
| Clean-install reproducibility | new empty venv → `pip install -r requirements.txt` → `pip check` → `pytest` | **No broken requirements; 24 / 24 passed** |
| Saved-output validation | independent script that recomputes metrics, SHAP and LIME from the saved model and compares them with every saved file | **35 / 35 checks passed** |
| Real-browser click-through | Playwright driving installed Microsoft Edge against `streamlit run app.py` | **34 / 34 checks passed**, 0 browser console errors |
| Runtime warnings | `python -W default train_model.py` / `evaluate.py` | **0 warnings** (no deprecation or future warnings) |
| Dependency consistency | `pip check` | **No broken requirements** |

## 2. Assignment deliverables

| Requirement | Status | Evidence |
|---|---|---|
| Clinical prediction from biomarker data | ✅ | Random Forest, 300 trees, `models/clinxai_rf_bundle.joblib` |
| Malignant = 1 / benign = 0 re-encoding | ✅ | Verified against sklearn `target == 0` for all 569 rows; `classes_ == [0, 1]` |
| Stratified 80/20 split, `random_state=42`, no leakage | ✅ | 455 / 114, disjoint indices; LIME statistics and the baseline scaler are fitted on training data only |
| Feature names and order preserved | ✅ | `feature_names_in_` equals sklearn order; dict inputs are re-ordered by name |
| Accuracy, precision, recall, F1, ROC-AUC, confusion matrix | ✅ | `outputs/metrics/metrics.json/.csv`, `confusion_matrix.png`, `roc_curve.png` |
| Logistic Regression baseline | ✅ | Included in metrics and ROC |
| LIME individual explanations (fixed seed, malignant class) | ✅ | `lime_case*.png`; reproducible with seed 42 |
| SHAP global bar, beeswarm, local waterfall, local force, table | ✅ | `shap_global_importance.png`, `shap_summary_beeswarm.png`, `shap_waterfall_*`, `shap_force_*.png/.html` |
| SHAP additivity check | ✅ | Max error 4.44e-16 over 114 test patients |
| LIME vs SHAP comparison (top-5, Jaccard, Spearman, direction, stability) | ✅ | `test_set_lime_vs_shap.csv`, `lime_vs_shap_case*.png` |
| 3–5 programmatic case studies saved to CSV/JSON | ✅ | 5 / 5 found: `case_studies.csv`, `case_studies.json` |
| Streamlit dashboard, 7 sections | ✅ | Browser-verified (section 3) |
| Tests for all listed areas | ✅ | 24 tests (section 1) |
| Architecture diagram | ✅ | `architecture.png` |
| README with Windows install and demo script; project summary | ✅ | `README.md`, `docs/PROJECT_SUMMARY.md` |

## 3. Streamlit tabs (real Edge browser)

| Tab | Images rendered (all loaded, none broken) | Exceptions / error alerts | Interaction verified |
|---|---|---|---|
| Overview | 1 (architecture) | 0 | Title, dataset, scope note, disclaimer visible |
| Diagnostic Prediction | 1 (risk gauge) | 0 | #70 → P = 1.000 Malignant; what-if on #100: `worst area` 906.5 → 500 flips to **Benign, P = 0.363** |
| LIME Explanation | 1 | 0 | Updates on patient change (#86 R² = 0.03); seed 7 gives R² 0.02; seed 42 again gives 0.03 |
| SHAP Explanation | 4 (bar, beeswarm, waterfall, force) | 0 | Base 0.375; sum of SHAP changes +0.625 → −0.078 on switching #70 → #86; interactive force plot renders an SVG inside the iframe; "(adjusted values)" label and base + sum = 0.363 after the what-if |
| LIME vs SHAP | 1 | 0 | #70: 5/5 overlap; #86: 0/5 overlap, 4 direction disagreements; stability toggle for #86 = 0.39 (matches saved case study) |
| Model Evaluation | 2 (confusion matrix, ROC) | 0 | 0.9737 / 1.0000 / 0.9286 / 0.9630 / 0.9944 displayed |
| Case Studies | 6 (overview + 5 comparisons) | 0 | All 5 cases listed; "Open patient #73 in all tabs" switches the whole app to #73 (P = 0.160; 1/5 overlap; 4 disagreements) |

## 4. Model evaluation (recomputed from the saved model and identical to the saved files)

Positive class: **Malignant (1)** · threshold 0.5 · test set 114 patients (42 malignant / 72 benign)

| Model | Accuracy | Precision | Recall | Specificity | F1 | ROC-AUC | TN | FP | FN | TP |
|---|---|---|---|---|---|---|---|---|---|---|
| Random Forest | 0.9737 | 1.0000 | 0.9286 | 1.0000 | 0.9630 | 0.9944 | 72 | 0 | 3 | 39 |
| Logistic Regression (baseline) | 0.9649 | 0.9750 | 0.9286 | 0.9861 | 0.9512 | 0.9960 | 71 | 1 | 3 | 39 |

Consistency checks passed:
- The confusion matrix sums to 114, and TP + FN = 42 actual malignant.
- Accuracy = (TP + TN) / 114, precision = TP / (TP + FP), and recall = TP / (TP + FN).
- `metrics.csv` agrees with `metrics.json`.

The Random Forest's 5-fold CV ROC-AUC on the training set is 0.9880 ± 0.0073.

## 5. LIME and SHAP explain the malignant class

| Check | Result |
|---|---|
| SHAP values used are the class-1 slice of TreeExplainer output `(n, 30, 2)` | ✅ exact match |
| SHAP class-1 = −(class-0) | ✅ (binary consistency) |
| base + ΣSHAP = `predict_proba[:, 1]` | ✅ max error 4.44e-16 |
| SHAP base value | 0.3747 (probability units) |
| Highest-risk patient: total SHAP > 0; lowest-risk: < 0 | ✅ |
| LIME explains label 1; top-5 weight sum +0.513 (highest-risk) / −0.301 (lowest-risk) | ✅ signs as expected |
| LIME `model_proba` equals the Random Forest's P(malignant) | ✅ |

## 6. Case studies (each re-run independently and found identical to the saved outputs)

| # | Case | Patient | P(mal) | Actual | Predicted | Top-5 overlap | Spearman ρ | Direction disagreements | LIME R² |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Clearly malignant | 70 | 1.000 | Malignant | Malignant | 5/5 | 0.90 | — | 0.63 |
| 2 | Clearly benign | 74 | 0.000 | Benign | Benign | 5/5 | 0.83 | — | 0.17 |
| 3 | Borderline | 100 | 0.513 | Malignant | Malignant | 2/5 | 0.60 | area error, worst perimeter | 0.05 |
| 4 | Ranking divergence | **86** | 0.297 | Malignant | **Benign (false negative)** | 0/5 | 0.27 | worst area, worst perimeter, mean concave points, area error | 0.03 |
| 5 | Direction disagreement | **73** | 0.160 | Malignant | **Benign (false negative)** | 1/5 | 0.39 | worst area, worst perimeter, mean concavity, mean concave points | 0.06 |

Each case meets its selection rule:
- Case 1 has the maximum P(malignant) and case 2 the minimum.
- Case 3 is the patient closest to 0.5.
- #86 has the lowest top-5 Jaccard among the remaining patients.
- #73 has the most direction disagreements among the patients left after that.

Both #86 and #73 are confirmed false negatives. They are 2 of the model's 3 false negatives.

Aggregate over the 114 test patients:
- Mean top-5 Jaccard 0.62, and mean top-5 overlap 3.66/5.
- Mean Spearman ρ 0.70.
- 28.9 % of patients have at least one direction disagreement.
- Mean LIME local R² 0.27.

## 7. Saved artefacts (all present and valid)

- **Figures:** 26 PNGs, each opened and decoded successfully, with no stray files:
  - architecture, case_study_agreement, confusion_matrix, roc_curve, shap_global_importance, shap_summary_beeswarm
  - for each of the 5 cases: LIME, SHAP waterfall, SHAP force and LIME-vs-SHAP
- **Interactive:** 5 SHAP force-plot HTML files, each with the SHAP JavaScript embedded.
- **Metrics:** `metrics.json`, `metrics.csv`, `dataset_overview.csv` (30 features), `shap_additivity.json`,
  `shap_global_importance.csv`.
- **Case studies:** `case_studies.csv`, `case_studies.json`, `test_set_lime_vs_shap.csv` (114 rows; P(malignant) matches
  the model).

## 8. Changes made during verification (presentation only)
Three figure-readability fixes in `src/visualization.py`. None changes any number, metric or behaviour:
1. LIME-vs-SHAP chart: the SHAP x-axis tick labels overlapped (visible for patient #73). The number of ticks is now limited.
2. Case-study agreement chart: added value labels, so patient #86's Jaccard of 0.00 is visibly labelled instead of
   looking like a missing bar.
3. Static force plot: values are formatted as `worst area = 1866` instead of `1.87e+03`.

Outputs were regenerated with `evaluate.py`. Afterwards the tests (24/24), the output validation (35/35) and the
browser checks (34/34) were all re-run and passed.

## 9. Outstanding limitations and notes

**Verification coverage**
- The browser check used Edge (Chromium) on Windows, headless, at 1500 × 1000. Firefox, Safari, mobile layouts and
  projector resolutions were not tested.
- The verification scripts (output validator, browser click-through) were run from a temporary folder and are not part
  of the project. Playwright is installed in `.venv` for verification only and is **not** in `requirements.txt`.

**Runtime behaviour**
- When a browser tab disconnects, the Streamlit server on Windows may log
  `ConnectionResetError [WinError 10054]`. This is harmless asyncio noise and does not affect the app.
- On first launch the app takes about 6–8 s to load the model and compute SHAP for the test set. A new LIME explanation
  takes about 1 s, and the 5-seed stability check about 5 s. Results are cached afterwards.
- The sidebar dropdown truncates long patient labels when closed. The full label shows when it is opened.

**Scientific limitations** (unchanged; also stated in the app and the summary)
- Probabilities are uncalibrated vote fractions.
- Small single-centre dataset, one 114-patient test split, no external validation.
- LIME depends on the seed and number of samples, and its average local R² is low (0.27).
- LIME and SHAP magnitudes are not comparable; only ranks and signs are compared.
- Correlated size features (radius / perimeter / area) split credit in different ways in the two methods.
- Tree-path-dependent SHAP explains the model, not biology.
- The system is tabular only and processes no raw images.
- Jaccard and Spearman measure agreement between explainers, not clinical validity.

## 10. Readiness

**The project is ready for report generation.** All assignment deliverables are implemented. All automated, output,
clean-install and real-browser checks pass. The saved metrics, figures and case-study files are internally consistent
and reproduce exactly from the saved model with seed 42.
