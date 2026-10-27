"""Central configuration: paths, seeds and class conventions used across ClinXAI."""
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT_DIR / "models"
OUTPUTS_DIR = ROOT_DIR / "outputs"
FIGURES_DIR = OUTPUTS_DIR / "figures"
METRICS_DIR = OUTPUTS_DIR / "metrics"
CASE_STUDIES_DIR = OUTPUTS_DIR / "case_studies"

MODEL_PATH = MODELS_DIR / "clinxai_rf_bundle.joblib"

RANDOM_STATE = 42
TEST_SIZE = 0.20
DECISION_THRESHOLD = 0.5

# Application-wide class convention (sklearn's raw dataset uses malignant=0, benign=1).
# ClinXAI re-encodes the target so that the positive clinical-risk class is malignant.
POSITIVE_CLASS = 1
CLASS_NAMES = ["Benign", "Malignant"]  # index == encoded label
MALIGNANT_LABEL = 1
BENIGN_LABEL = 0

RF_PARAMS = {
    "n_estimators": 300,
    "max_depth": None,
    "min_samples_leaf": 1,
    "class_weight": None,
    "random_state": RANDOM_STATE,
    "n_jobs": -1,
}

LIME_NUM_SAMPLES = 5000
LIME_NUM_FEATURES = 10
LIME_STABILITY_SEEDS = (0, 1, 2, 3, 4)
TOP_K = 5


def ensure_dirs() -> None:
    for d in (MODELS_DIR, FIGURES_DIR, METRICS_DIR, CASE_STUDIES_DIR):
        d.mkdir(parents=True, exist_ok=True)
