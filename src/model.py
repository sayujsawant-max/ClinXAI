"""Model training, evaluation, persistence and prediction helpers."""
from __future__ import annotations

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.config import (
    CLASS_NAMES,
    DECISION_THRESHOLD,
    MALIGNANT_LABEL,
    MODEL_PATH,
    RANDOM_STATE,
    RF_PARAMS,
)
from src.data_loader import DataSplit


def train_random_forest(X_train: pd.DataFrame, y_train: pd.Series) -> RandomForestClassifier:
    model = RandomForestClassifier(**RF_PARAMS)
    model.fit(X_train, y_train)
    assert list(model.classes_) == [0, 1], "Expected classes [0=benign, 1=malignant]"
    return model


def train_logistic_baseline(X_train: pd.DataFrame, y_train: pd.Series):
    """Interpretable baseline. Scaling lives inside the pipeline, so it is fit on training data only."""
    pipe = make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000, random_state=RANDOM_STATE))
    pipe.fit(X_train, y_train)
    return pipe


def malignant_proba(model, X: pd.DataFrame) -> np.ndarray:
    """P(malignant) using the column that corresponds to label 1, not a positional guess."""
    col = list(model.classes_).index(MALIGNANT_LABEL)
    return model.predict_proba(X)[:, col]


def evaluate_classifier(model, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    proba = malignant_proba(model, X_test)
    pred = (proba >= DECISION_THRESHOLD).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, pred, labels=[0, 1]).ravel()
    return {
        "positive_class": f"{CLASS_NAMES[MALIGNANT_LABEL]} (label {MALIGNANT_LABEL})",
        "decision_threshold": DECISION_THRESHOLD,
        "accuracy": float(accuracy_score(y_test, pred)),
        "precision": float(precision_score(y_test, pred, pos_label=MALIGNANT_LABEL)),
        "recall_sensitivity": float(recall_score(y_test, pred, pos_label=MALIGNANT_LABEL)),
        "specificity": float(tn / (tn + fp)),
        "f1": float(f1_score(y_test, pred, pos_label=MALIGNANT_LABEL)),
        "roc_auc": float(roc_auc_score(y_test, proba)),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }


def cross_validated_auc(model_factory, X_train: pd.DataFrame, y_train: pd.Series) -> dict:
    """5-fold stratified CV on the training set only (no test data involved)."""
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    scores = cross_val_score(model_factory(), X_train, y_train, cv=cv, scoring="roc_auc")
    return {"cv_roc_auc_mean": float(scores.mean()), "cv_roc_auc_std": float(scores.std())}


def roc_points(model, X_test, y_test):
    fpr, tpr, _ = roc_curve(y_test, malignant_proba(model, X_test))
    return fpr, tpr


def save_bundle(model, baseline, split: DataSplit, metrics: dict, path=MODEL_PATH) -> None:
    """Persist the model together with everything needed to reproduce explanations."""
    bundle = {
        "model": model,
        "baseline": baseline,
        "feature_names": split.feature_names,
        "class_names": CLASS_NAMES,
        "positive_class": MALIGNANT_LABEL,
        "X_train": split.X_train,
        "y_train": split.y_train,
        "X_test": split.X_test,
        "y_test": split.y_test,
        "metrics": metrics,
        "versions": {"sklearn": sklearn.__version__},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, path)


def load_bundle(path=MODEL_PATH) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Model bundle not found at {path}. Run `python train_model.py` first.")
    bundle = joblib.load(path)
    model = bundle["model"]
    if list(model.feature_names_in_) != bundle["feature_names"]:
        raise ValueError("Feature ordering mismatch between model and saved metadata")
    return bundle
