# ClinXAI — Project Summary (report evidence)

All numbers below were produced by `train_model.py` and `evaluate.py` (seed 42). Source files are in `outputs/`.

## 1. Problem and objective
Complex ensembles such as Random Forests are often more accurate than inherently interpretable models, but they are
opaque. That is a trust and accountability problem in healthcare. ClinXAI trains a Random Forest to predict biopsy
malignancy. It explains every prediction with LIME and SHAP, and it measures how far the two explainers agree. It is
an educational system and makes no clinical claims.

## 2. Data
- Breast Cancer Wisconsin (Diagnostic), `sklearn.datasets.load_breast_cancer()`.
- 569 patients × 30 features (10 nuclear measurements × mean / standard error / worst) from digitised FNA images.
- 212 malignant, 357 benign. Labels are re-mapped to **malignant = 1 (positive)** and benign = 0.
- Stratified 80/20 split with `random_state=42`: 455 training and 114 test patients (42 malignant / 72 benign in the
  test set).
- Leakage control: the model, the LIME sampling statistics and the baseline scaler are fitted on training data only.
- Per-feature table: `outputs/metrics/dataset_overview.csv`.

## 3. Model performance (test set, threshold 0.5)
| Model | Accuracy | Precision | Recall | Specificity | F1 | ROC-AUC |
|---|---|---|---|---|---|---|
| Random Forest | 0.9737 | 1.0000 | 0.9286 | 1.0000 | 0.9630 | 0.9944 |
| Logistic Regression (baseline) | 0.9649 | 0.9750 | 0.9286 | 0.9861 | 0.9512 | 0.9960 |

- Random Forest confusion matrix: TN 72, FP 0, FN 3, TP 39.
- 5-fold CV ROC-AUC on the training set: 0.9880 ± 0.0073.
- **Interpretability trade-off:** on this dataset the transparent baseline is roughly as good as the forest (higher
  AUC, slightly lower accuracy). The forest's small accuracy gain comes at the cost of needing post-hoc explanation.
- Figures: `confusion_matrix.png`, `roc_curve.png`.

## 4. SHAP
- `shap.TreeExplainer` in tree-path-dependent mode. For a scikit-learn Random Forest the raw tree output is the class
  probability, so base value, SHAP values and `predict_proba` are all in probability units.
- Base value E[P(malignant)] = 0.3747. The additivity error is at most 4.4e-16 over all 114 test patients
  (`shap_additivity.json`).
- Top global features by mean |SHAP|: worst area (0.067), worst perimeter (0.060), worst concave points (0.059),
  mean concave points (0.044).
- Figures: `shap_global_importance.png` (global bar), `shap_summary_beeswarm.png`, and
  `shap_waterfall_case*.png` / `shap_force_case*.png|.html` (local).

## 5. LIME
- `LimeTabularExplainer` with quartile discretisation, statistics from the training set, 5000 perturbation samples, and
  a fixed seed (a fresh explainer is built per explanation, so results are reproducible).
- It explains label 1, P(malignant). Positive weights push toward malignant.
- The mean local surrogate R² over the test set is **0.27**, so the linear surrogate often fits the forest poorly.
- Figures: `lime_case*.png`.

## 6. LIME vs SHAP over all 114 test patients
| Measure | Value |
|---|---|
| Mean top-5 overlap | 3.66 / 5 |
| Mean top-5 Jaccard | 0.62 |
| Mean Spearman ρ of \|attribution\| (30 features) | 0.70 |
| Patients with ≥1 direction disagreement (top-5 union) | 28.9 % |

These are agreement measures between explanation methods, **not** clinical validation metrics. LIME weights and SHAP
values have different meanings (surrogate coefficients vs. Shapley attributions), so only ranks and signs are compared.
Per-patient data: `outputs/case_studies/test_set_lime_vs_shap.csv`.

## 7. Case studies (selected programmatically from the test set)
| # | Case | Patient | P(mal) | Actual | Top-5 overlap | Spearman | Direction disagreements | LIME R² | LIME seed stability* |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Clearly malignant | 70 | 1.000 | Malignant | 5/5 | 0.90 | none | 0.63 | 0.87 |
| 2 | Clearly benign | 74 | 0.000 | Benign | 5/5 | 0.83 | none | 0.17 | 1.00 |
| 3 | Borderline | 100 | 0.513 | Malignant | 2/5 | 0.60 | area error, worst perimeter | 0.05 | 0.48 |
| 4 | Ranking divergence | 86 | 0.297 | Malignant (**missed**) | 0/5 | 0.27 | worst area, worst perimeter, mean concave points, area error | 0.03 | 0.39 |
| 5 | Direction disagreement | 73 | 0.160 | Malignant (**missed**) | 1/5 | 0.39 | worst area, worst perimeter, mean concavity, mean concave points | 0.06 | 0.60 |

\*Mean pairwise top-5 Jaccard of LIME across seeds 0–4. SHAP is deterministic.

**Key observations**
1. On confident predictions (cases 1–2) the two explainers fully agree on the top-5 features: the size and concavity
   "worst" features.
2. Agreement collapses near the decision boundary and on false negatives (cases 3–5). In those cases LIME's local
   R² is ≤ 0.06 and its own top-5 set changes noticeably between random seeds.
3. Both divergence cases are malignant tumours the model classified as benign. These are the clinically most costly
   errors, and they are where a single explanation would be least trustworthy. That supports showing both methods
   together.

**Likely causes of divergence:** LIME linearises a non-linear decision surface using discretised bins. Its independent
perturbations create unrealistic feature combinations. Radius, perimeter and area are highly correlated, so both
methods split credit among them differently. SHAP follows the forest's actual split structure.

Outputs: `case_studies.csv`, `case_studies.json`, `lime_vs_shap_case*.png`, `case_study_agreement.png`.

## 8. Limitations
- Probabilities are uncalibrated vote fractions.
- The dataset is small and single-centre, evaluated on one split with no external validation.
- LIME results depend on the seed and sample count, and its local fidelity is low on average.
- Tree-path-dependent SHAP describes the model, not causal biology.
- The system is tabular only; it does not process raw images.

## 9. Future scope
- Fuse image and tabular data, for example a CNN on cytology images plus the tabular features, explained with Grad-CAM
  and SHAP.
- Calibrate probabilities (Platt or isotonic) and report decision-curve analysis.
- Try KernelSHAP or interventional SHAP with a background set, and correlation-aware explainers.
- Run a user study with clinicians on whether the explanations are useful.

## 10. Architecture
See `outputs/figures/architecture.png`: data → stratified split → Random Forest (+ baseline) → LIME / SHAP /
evaluation → comparison and case studies → Streamlit dashboard.
