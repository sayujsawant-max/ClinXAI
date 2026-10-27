"""Dataset loading, label re-encoding, validation, splitting and patient-input validation."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

from src.config import BENIGN_LABEL, MALIGNANT_LABEL, RANDOM_STATE, TEST_SIZE

EXPECTED_N_SAMPLES = 569
EXPECTED_N_FEATURES = 30


@dataclass
class DataSplit:
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    feature_names: list[str]


def load_dataset() -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Load Breast Cancer Wisconsin (Diagnostic) and re-encode so malignant = 1, benign = 0.

    sklearn ships the target as 0 = malignant, 1 = benign. The mapping is derived from
    ``target_names`` rather than hard-coded, then asserted.
    """
    raw = load_breast_cancer(as_frame=True)
    X = raw.data.copy()
    raw_target = raw.target.to_numpy()
    target_names = list(raw.target_names)
    raw_malignant = target_names.index("malignant")
    raw_benign = target_names.index("benign")

    y = pd.Series(
        np.where(raw_target == raw_malignant, MALIGNANT_LABEL, BENIGN_LABEL),
        index=X.index,
        name="diagnosis_malignant",
    )
    # Verify the re-encoding against sklearn's own labels.
    assert np.all((raw_target == raw_malignant) == (y.to_numpy() == MALIGNANT_LABEL))
    assert np.all((raw_target == raw_benign) == (y.to_numpy() == BENIGN_LABEL))

    validate_dataset(X, y)
    return X, y, list(X.columns)


def validate_dataset(X: pd.DataFrame, y: pd.Series) -> None:
    if X.shape != (EXPECTED_N_SAMPLES, EXPECTED_N_FEATURES):
        raise ValueError(f"Unexpected dataset shape {X.shape}")
    if X.isna().any().any():
        raise ValueError("Dataset contains missing values")
    if not np.isfinite(X.to_numpy()).all():
        raise ValueError("Dataset contains non-finite values")
    if set(np.unique(y)) != {BENIGN_LABEL, MALIGNANT_LABEL}:
        raise ValueError("Target must be binary {0, 1}")
    if len(set(X.columns)) != X.shape[1]:
        raise ValueError("Duplicate feature names")


def split_data(X: pd.DataFrame, y: pd.Series) -> DataSplit:
    """Stratified 80/20 split. All fitting (model, LIME statistics) uses the training part only."""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )
    return DataSplit(X_train, X_test, y_train, y_test, list(X.columns))


def dataset_overview(X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
    """Per-feature summary table for the report."""
    desc = X.describe().T[["mean", "std", "min", "max"]]
    desc["mean_malignant"] = X[y == MALIGNANT_LABEL].mean()
    desc["mean_benign"] = X[y == BENIGN_LABEL].mean()
    desc.index.name = "feature"
    return desc.round(4)


def validate_patient_input(values, feature_names: list[str]) -> pd.DataFrame:
    """Validate a single patient's biomarker values and return a correctly ordered 1-row frame.

    Accepts a dict (feature -> value), a pandas Series, or a 1-D sequence in training order.
    Raises ValueError for missing/extra features, non-numeric, non-finite or negative values
    (all 30 features are non-negative physical measurements).
    """
    if isinstance(values, pd.DataFrame):
        if len(values) != 1:
            raise ValueError("Exactly one patient row is required")
        values = values.iloc[0]
    if isinstance(values, (dict, pd.Series)):
        keys = list(values.keys())
        missing = [f for f in feature_names if f not in keys]
        extra = [k for k in keys if k not in feature_names]
        if missing:
            raise ValueError(f"Missing features: {missing}")
        if extra:
            raise ValueError(f"Unknown features: {extra}")
        ordered = [values[f] for f in feature_names]
    else:
        ordered = list(values)
        if len(ordered) != len(feature_names):
            raise ValueError(f"Expected {len(feature_names)} values, got {len(ordered)}")

    try:
        arr = np.asarray(ordered, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"All biomarker values must be numeric: {exc}") from exc
    if not np.isfinite(arr).all():
        bad = [f for f, v in zip(feature_names, arr) if not np.isfinite(v)]
        raise ValueError(f"Non-finite values for: {bad}")
    if (arr < 0).any():
        bad = [f for f, v in zip(feature_names, arr) if v < 0]
        raise ValueError(f"Negative values are not physically valid for: {bad}")
    return pd.DataFrame([arr], columns=feature_names)


def out_of_range_features(row: pd.DataFrame, X_train: pd.DataFrame) -> list[str]:
    """Features whose value lies outside the training range (extrapolation warning)."""
    lo, hi = X_train.min(), X_train.max()
    r = row.iloc[0]
    return [f for f in X_train.columns if r[f] < lo[f] or r[f] > hi[f]]
