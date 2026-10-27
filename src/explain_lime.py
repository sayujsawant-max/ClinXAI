"""LIME local explanations for the malignant-class probability."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from lime.lime_tabular import LimeTabularExplainer

from src.config import CLASS_NAMES, LIME_NUM_SAMPLES, MALIGNANT_LABEL, RANDOM_STATE


@dataclass
class LimeResult:
    table: pd.DataFrame          # feature, rule, weight, abs_weight, rank (sorted by |weight|)
    weights: pd.Series           # weight per feature, indexed by feature name (training order)
    intercept: float             # surrogate intercept for the malignant class
    local_pred: float            # surrogate's prediction at the instance
    score: float                 # R^2 of the weighted surrogate fit (local fidelity)
    model_proba: float           # Random Forest P(malignant) for the instance
    seed: int


def build_lime_explainer(X_train: pd.DataFrame, seed: int = RANDOM_STATE) -> LimeTabularExplainer:
    """Fit LIME's sampling/discretisation statistics on TRAINING data only."""
    return LimeTabularExplainer(
        training_data=X_train.to_numpy(),
        feature_names=list(X_train.columns),
        class_names=CLASS_NAMES,
        mode="classification",
        discretize_continuous=True,
        discretizer="quartile",
        random_state=seed,
    )


def make_predict_fn(model, feature_names: list[str]):
    """LIME passes bare numpy arrays; rebuild a DataFrame so column order/name match training."""
    assert list(model.classes_) == [0, 1]

    def predict_fn(arr: np.ndarray) -> np.ndarray:
        return model.predict_proba(pd.DataFrame(arr, columns=feature_names))

    return predict_fn


def explain_patient_lime(
    model,
    X_train: pd.DataFrame,
    patient: pd.DataFrame | pd.Series,
    seed: int = RANDOM_STATE,
    num_samples: int = LIME_NUM_SAMPLES,
) -> LimeResult:
    """Explain P(malignant) for one patient.

    A fresh explainer is created per call with a fixed seed so the explanation is exactly
    reproducible (re-using one explainer would advance its RNG between calls).
    All features are requested so LIME and SHAP can be compared over the full feature set.
    """
    feature_names = list(X_train.columns)
    row = patient.iloc[0] if isinstance(patient, pd.DataFrame) else patient
    x = row[feature_names].to_numpy(dtype=float)

    explainer = build_lime_explainer(X_train, seed)
    exp = explainer.explain_instance(
        x,
        make_predict_fn(model, feature_names),
        labels=(MALIGNANT_LABEL,),
        num_features=len(feature_names),
        num_samples=num_samples,
    )
    idx_weights = exp.as_map()[MALIGNANT_LABEL]
    rules = exp.as_list(label=MALIGNANT_LABEL)  # same ordering as as_map
    records = [
        {"feature": feature_names[i], "rule": rule, "weight": float(w)}
        for (i, w), (rule, _) in zip(idx_weights, rules)
    ]
    table = pd.DataFrame(records)
    table["abs_weight"] = table["weight"].abs()
    table = table.sort_values("abs_weight", ascending=False).reset_index(drop=True)
    table["rank"] = np.arange(1, len(table) + 1)
    table["direction"] = np.where(table["weight"] > 0, "→ Malignant", "→ Benign")

    weights = table.set_index("feature")["weight"].reindex(feature_names).fillna(0.0)
    model_proba = float(model.predict_proba(pd.DataFrame([x], columns=feature_names))[0, MALIGNANT_LABEL])
    return LimeResult(
        table=table,
        weights=weights,
        intercept=float(exp.intercept[MALIGNANT_LABEL]),
        local_pred=float(np.ravel(exp.local_pred)[0]),
        score=float(exp.score),
        model_proba=model_proba,
        seed=seed,
    )
