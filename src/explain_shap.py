"""SHAP TreeExplainer attributions for the malignant-class probability."""
from __future__ import annotations

import numpy as np
import pandas as pd
import shap

from src.config import MALIGNANT_LABEL


def build_tree_explainer(model) -> shap.TreeExplainer:
    """TreeExplainer in its default 'tree_path_dependent' mode.

    No background dataset is needed: the expected value is taken from the training-sample
    coverage stored in each tree. For a scikit-learn Random Forest the trees' raw output is
    the class-probability average, so SHAP values, the base value and predict_proba all share
    probability units and satisfy base + sum(SHAP) == P(malignant).
    """
    return shap.TreeExplainer(model)


def _select_malignant(values, expected_value) -> tuple[np.ndarray, float]:
    """Normalise SHAP's version-dependent return formats to (n, n_features) for class 1."""
    ev = np.atleast_1d(np.asarray(expected_value, dtype=float))
    if isinstance(values, list):  # older SHAP: list of per-class arrays
        vals = np.asarray(values[MALIGNANT_LABEL])
        base = ev[MALIGNANT_LABEL]
    else:
        vals = np.asarray(values)
        if vals.ndim == 3:  # SHAP >= 0.45: (n_samples, n_features, n_classes)
            vals = vals[:, :, MALIGNANT_LABEL]
            base = ev[MALIGNANT_LABEL]
        elif vals.ndim == 2:  # single-output model
            base = ev[-1] if ev.size > 1 else ev[0]
        else:
            raise ValueError(f"Unexpected SHAP value shape {vals.shape}")
    return vals, float(base)


def compute_shap(explainer: shap.TreeExplainer, X: pd.DataFrame) -> shap.Explanation:
    """Return a 2-D shap.Explanation (malignant class) for the rows of X."""
    raw = explainer.shap_values(X)
    vals, base = _select_malignant(raw, explainer.expected_value)
    return shap.Explanation(
        values=vals,
        base_values=np.full(vals.shape[0], base),
        data=X.to_numpy(),
        feature_names=list(X.columns),
    )


def additivity_error(model, explanation: shap.Explanation, X: pd.DataFrame) -> float:
    """Max |base + sum(SHAP) - P(malignant)| over the rows of X."""
    reconstructed = explanation.base_values + explanation.values.sum(axis=1)
    proba = model.predict_proba(X)[:, MALIGNANT_LABEL]
    return float(np.max(np.abs(reconstructed - proba)))


def shap_table(explanation_row: shap.Explanation) -> pd.DataFrame:
    """Per-feature contribution table for a single patient, sorted by |SHAP|."""
    df = pd.DataFrame(
        {
            "feature": explanation_row.feature_names,
            "value": explanation_row.data,
            "shap_value": explanation_row.values,
        }
    )
    df["abs_shap"] = df["shap_value"].abs()
    df = df.sort_values("abs_shap", ascending=False).reset_index(drop=True)
    df["rank"] = np.arange(1, len(df) + 1)
    df["direction"] = np.where(df["shap_value"] > 0, "→ Malignant", "→ Benign")
    return df


def global_importance(explanation: shap.Explanation) -> pd.Series:
    """Mean |SHAP| per feature over the explained set (global importance)."""
    return (
        pd.Series(np.abs(explanation.values).mean(axis=0), index=explanation.feature_names)
        .sort_values(ascending=False)
    )
