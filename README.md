# ClinXAI — Transparent Clinical Diagnostics Using LIME and SHAP

**Course:** Trustworthy and Responsible AI (ADCOR1PC303) · **Domain:** Healthcare Systems / Societal Impact
**Syllabus mapping:** Module 1 — Interpretability trade-offs, LIME perturbations, SHAP game theory

> ⚠️ Research / educational demonstration only. Not a medical device. No clinical or treatment recommendations.

ClinXAI predicts whether a breast-tumour biopsy is **malignant (1)** or **benign (0)** with a Random Forest. It explains
each prediction with **LIME** (a local surrogate model) and **SHAP** (local and global Shapley attributions), then
measures where the two explanations agree and where they disagree.

## Live demo (Streamlit Community Cloud)
**Live app:** https://clinxai-8vkbnrgqqfnwa9gwa9tywa.streamlit.app/
Repository: https://github.com/sayujsawant-max/ClinXAI

The deployed app was checked in a real browser (Microsoft Edge): all seven tabs load with no errors, and it shows the
same results as the local build (accuracy 0.9737, recall 0.9286, ROC-AUC 0.9944; mean top-5 Jaccard 0.62).
Free Streamlit apps sleep after a period without visitors. If you see a "wake up" button, click it and the app
restarts in under a minute.

To deploy (one-time, about 5 minutes):
1. Sign in at https://share.streamlit.io with the GitHub account that owns this repository.
2. Choose **Create app**, then **Deploy a public app from GitHub**.
3. Set **Repository** to `sayujsawant-max/ClinXAI`, **Branch** to `main`, and **Main file path** to `app.py`.
4. Open **Advanced settings** and set **Python version** to **3.12** (the pinned `requirements.txt` was tested on 3.12).
5. Click **Deploy**. The first build installs the dependencies, which takes a few minutes. The app loads the bundled
   model from `models/`, or trains one automatically if the file is missing.

Verified before deployment: a clean Linux container (`python:3.12-slim`) installs `requirements.txt` with no conflicts,
passes all 24 tests, and serves the app (health check `ok`, HTTP 200).

## Scope (honest description)
- **Data:** the Breast Cancer Wisconsin (Diagnostic) dataset from `sklearn.datasets.load_breast_cancer()`: 569 patients
  × 30 numeric features computed from digitised images of fine-needle-aspirate cell nuclei.
- **Tabular only.** The app does **not** process raw images. "Multi-modal" here means two complementary *explanation*
  methods. Combining real images with tabular data is listed as future scope.
- **Label convention:** sklearn encodes malignant = 0. ClinXAI re-maps the labels on load, so **malignant = 1 = positive
  class** everywhere: in metrics, probabilities, LIME, SHAP and the UI. `tests/test_pipeline.py` checks this mapping.

## Project structure
```
ClinXAI/
  app.py                  Streamlit dashboard (7 tabs)
  train_model.py          train RF + LR baseline, metrics, confusion matrix, ROC, model bundle
  evaluate.py             SHAP global/local, LIME on every test patient, LIME-vs-SHAP, case studies
  requirements.txt
  src/
    config.py             paths, seeds, class convention
    data_loader.py        load/validate/re-encode, stratified split, patient-input validation
    model.py              training, evaluation, persistence, P(malignant)
    explain_lime.py       LimeTabularExplainer (fitted on training data, fixed seed)
    explain_shap.py       TreeExplainer, version-safe malignant-class selection, additivity check
    comparison.py         top-k Jaccard, Spearman, direction agreement, LIME stability, case selection
    visualization.py      all figures (Matplotlib, with SHAP plot fallbacks)
  models/                 clinxai_rf_bundle.joblib (model + feature order + split + metrics)
  outputs/figures/        PNG / HTML report figures
  outputs/metrics/        metrics.json/csv, dataset_overview.csv, shap_additivity.json, shap_global_importance.csv
  outputs/case_studies/   case_studies.csv/json, test_set_lime_vs_shap.csv
  tests/test_pipeline.py  24 tests (pipeline + Streamlit smoke test)
  docs/PROJECT_SUMMARY.md report-ready summary with real results
  .streamlit/config.toml  medical-style theme
```

## Installation (Windows PowerShell)
```powershell
cd C:\Projects\ClinXAI
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1          # if blocked: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
python -m pip install --upgrade pip
pip install -r requirements.txt
python train_model.py                 # ~10 s  -> models/ + metrics + confusion matrix + ROC
python evaluate.py                    # ~40 s  -> SHAP/LIME figures + case studies
python -m pytest -q                   # 24 tests
streamlit run app.py                  # opens http://localhost:8501
```
If the model file is missing, the app trains the model automatically on first launch. Run `evaluate.py` to populate the
Case Studies tab.

## Results (actual output: held-out test set of 114 patients, positive class = malignant)
| Model | Accuracy | Precision | Recall | Specificity | F1 | ROC-AUC | TN | FP | FN | TP |
|---|---|---|---|---|---|---|---|---|---|---|
| Random Forest (300 trees) | 0.9737 | 1.0000 | 0.9286 | 1.0000 | 0.9630 | 0.9944 | 72 | 0 | 3 | 39 |
| Logistic Regression baseline | 0.9649 | 0.9750 | 0.9286 | 0.9861 | 0.9512 | 0.9960 | 71 | 1 | 3 | 39 |

The Random Forest's 5-fold stratified CV ROC-AUC on the training set is 0.9880 ± 0.0073. SHAP additivity holds: the
maximum |base + ΣSHAP − P(malignant)| is 4.4e-16 across all 114 test patients.

See [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) for the LIME-vs-SHAP findings and case studies.

## 3-minute demonstration sequence
1. **Overview (20 s):** state the objective, the dataset, malignant = 1, and the disclaimer. Point to the architecture diagram.
2. **Model Evaluation (30 s):** accuracy 0.974, ROC-AUC 0.994, 0 false positives and **3 false negatives**. Mention the
   logistic-regression baseline.
3. **Diagnostic Prediction (30 s):** the app opens on *Patient #70 ★ Clearly malignant* (P = 1.000). Point to the
   gauge and the note that the probability is uncalibrated. Switch to *Patient #100 ★ Borderline* (P = 0.513), toggle
   *Adjust biomarkers*, and set `worst area` from 906.5 to 500: the prediction flips to Benign (P = 0.363), and every
   explanation tab updates.
4. **LIME (25 s):** show the red/blue rule bars and the local-fit R². Change the seed in the sidebar to show that LIME is
   sensitive to its random perturbations.
5. **SHAP (30 s):** global bar and beeswarm, then the patient's waterfall: base value 0.375 + contributions = P(malignant).
   Show the force plot.
6. **LIME vs SHAP (25 s):** for patient 70 the top-5 lists match exactly. Switch to *Patient #86 ★ Ranking divergence*
   (a missed malignancy): 0/5 shared features and 4 direction disagreements. Read out the reasons listed under the chart.
7. **Case Studies (20 s):** the 5 programmatically selected cases and the aggregate agreement (mean top-5 Jaccard 0.62).
   The key message: the explanations disagree most on borderline and misclassified patients, which are exactly the
   cases a clinician would most need to understand.
