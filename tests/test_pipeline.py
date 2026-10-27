"""End-to-end verification tests for ClinXAI.  Run:  python -m pytest -q"""
import sys
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from matplotlib.figure import Figure
from sklearn.datasets import load_breast_cancer

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import visualization as viz  # noqa: E402
from src.comparison import compare_explanations, jaccard, lime_stability, select_case_studies, top_k  # noqa: E402
from src.config import MALIGNANT_LABEL  # noqa: E402
from src.data_loader import load_dataset, split_data, validate_patient_input  # noqa: E402
from src.explain_lime import explain_patient_lime  # noqa: E402
from src.explain_shap import (  # noqa: E402
    _select_malignant,
    additivity_error,
    build_tree_explainer,
    compute_shap,
    global_importance,
    shap_table,
)
from src.model import (  # noqa: E402
    evaluate_classifier,
    load_bundle,
    malignant_proba,
    save_bundle,
    train_logistic_baseline,
    train_random_forest,
)

warnings.filterwarnings("ignore")


@pytest.fixture(scope="session")
def data():
    X, y, names = load_dataset()
    return X, y, names, split_data(X, y)


@pytest.fixture(scope="session")
def model(data):
    split = data[3]
    return train_random_forest(split.X_train, split.y_train)


@pytest.fixture(scope="session")
def shap_test(data, model):
    return compute_shap(build_tree_explainer(model), data[3].X_test)


# ------------------------------------------------------------------ data
def test_dataset_loading(data):
    X, y, names, _ = data
    assert X.shape == (569, 30)
    assert len(names) == 30
    assert not X.isna().any().any()
    assert set(y.unique()) == {0, 1}


def test_malignant_benign_mapping(data):
    X, y, _, _ = data
    raw = load_breast_cancer()
    assert list(raw.target_names) == ["malignant", "benign"]  # sklearn: 0 = malignant
    assert np.array_equal(y.to_numpy() == 1, raw.target == 0)
    assert int(y.sum()) == 212 and int((y == 0).sum()) == 357
    # Clinical sanity: malignant nuclei are larger on average.
    assert X.loc[y == 1, "mean radius"].mean() > X.loc[y == 0, "mean radius"].mean()


def test_feature_ordering(data, model):
    X, _, names, split = data
    assert names == list(load_breast_cancer().feature_names)
    assert list(split.X_train.columns) == names and list(split.X_test.columns) == names
    assert list(model.feature_names_in_) == names
    # A shuffled dict is re-ordered into training order.
    row = split.X_test.iloc[0]
    shuffled = dict(reversed(list(row.items())))
    assert list(validate_patient_input(shuffled, names).columns) == names
    np.testing.assert_allclose(validate_patient_input(shuffled, names).iloc[0].to_numpy(), row.to_numpy())


def test_split_stratified_without_leakage(data):
    _, y, _, split = data
    assert len(split.X_train) == 455 and len(split.X_test) == 114
    assert set(split.X_train.index).isdisjoint(split.X_test.index)
    assert abs(split.y_train.mean() - split.y_test.mean()) < 0.02
    assert abs(split.y_test.mean() - y.mean()) < 0.02


# ------------------------------------------------------------------ model
def test_model_prediction_and_probability_range(data, model):
    split = data[3]
    assert list(model.classes_) == [0, 1]
    proba = model.predict_proba(split.X_test)
    assert proba.shape == (114, 2)
    assert np.all((proba >= 0) & (proba <= 1))
    np.testing.assert_allclose(proba.sum(axis=1), 1.0)
    p_mal = malignant_proba(model, split.X_test)
    np.testing.assert_allclose(p_mal, proba[:, 1])
    # predict() and the 0.5 threshold on P(malignant) agree (exact ties at 0.5 excluded)
    untied = p_mal != 0.5
    assert np.array_equal(model.predict(split.X_test)[untied], (p_mal[untied] > 0.5).astype(int))


def test_metrics_use_malignant_as_positive(data, model):
    split = data[3]
    m = evaluate_classifier(model, split.X_test, split.y_test)
    cm = m["confusion_matrix"]
    assert cm["tp"] + cm["fn"] == int(split.y_test.sum())  # actual malignant count
    assert m["recall_sensitivity"] == pytest.approx(cm["tp"] / (cm["tp"] + cm["fn"]))
    for k in ["accuracy", "precision", "recall_sensitivity", "f1", "roc_auc"]:
        assert 0.0 <= m[k] <= 1.0


def test_bundle_roundtrip(data, model, tmp_path):
    split = data[3]
    baseline = train_logistic_baseline(split.X_train, split.y_train)
    path = tmp_path / "bundle.joblib"
    save_bundle(model, baseline, split, {"ok": True}, path=path)
    b = load_bundle(path)
    assert b["feature_names"] == split.feature_names and b["positive_class"] == MALIGNANT_LABEL
    np.testing.assert_allclose(b["model"].predict_proba(split.X_test), model.predict_proba(split.X_test))


# ------------------------------------------------------------------ LIME
def test_lime_explanation(data, model):
    split = data[3]
    patient = split.X_test.iloc[[0]]
    res = explain_patient_lime(model, split.X_train, patient, seed=42, num_samples=1000)
    assert len(res.table) == 30 and list(res.weights.index) == split.feature_names
    assert res.model_proba == pytest.approx(malignant_proba(model, patient)[0])
    assert 0.0 <= res.local_pred <= 1.5
    # Reproducible with the same seed
    res2 = explain_patient_lime(model, split.X_train, patient, seed=42, num_samples=1000)
    pd.testing.assert_series_equal(res.weights, res2.weights)


def test_lime_explains_malignant_class(data, model):
    """For a confidently malignant patient the strongest LIME weights should point toward malignant."""
    split = data[3]
    p = malignant_proba(model, split.X_test)
    patient = split.X_test.iloc[[int(np.argmax(p))]]
    res = explain_patient_lime(model, split.X_train, patient, num_samples=1000)
    assert res.table.head(5)["weight"].sum() > 0


# ------------------------------------------------------------------ SHAP
def test_shap_explanation_shape(data, shap_test):
    assert shap_test.values.shape == (114, 30)
    assert list(shap_test.feature_names) == data[2]
    assert len(global_importance(shap_test)) == 30
    tbl = shap_table(shap_test[0])
    assert tbl["abs_shap"].is_monotonic_decreasing


def test_shap_additivity(data, model, shap_test):
    X_test = data[3].X_test
    assert additivity_error(model, shap_test, X_test) < 1e-6
    i = int(np.argmax(malignant_proba(model, X_test)))
    assert shap_test.values[i].sum() > 0  # high-risk patient: contributions push above the base rate


def test_shap_format_normalisation():
    vals = np.arange(12, dtype=float).reshape(2, 3, 2)
    v3, b3 = _select_malignant(vals, [0.6, 0.4])
    np.testing.assert_array_equal(v3, vals[:, :, 1])
    assert b3 == pytest.approx(0.4)
    vl, bl = _select_malignant([vals[:, :, 0], vals[:, :, 1]], np.array([0.6, 0.4]))
    np.testing.assert_array_equal(vl, vals[:, :, 1])
    assert bl == pytest.approx(0.4)


# ------------------------------------------------------------------ comparison
def test_comparison_identical_and_opposite():
    idx = [f"f{i}" for i in range(10)]
    w = pd.Series(np.linspace(1, -0.5, 10), index=idx)
    same = compare_explanations(w, w)
    assert same["jaccard_top_k"] == 1.0 and same["spearman_abs_all_features"] == pytest.approx(1.0)
    assert same["direction_disagreements_union"] == []
    flipped = compare_explanations(-w, w)
    assert flipped["jaccard_top_k"] == 1.0
    assert set(flipped["direction_disagreements_union"]) == set(top_k(w))
    assert jaccard(["a", "b"], ["b", "c"]) == pytest.approx(1 / 3)


def test_case_selection():
    summary = pd.DataFrame({
        "patient_id": [1, 2, 3, 4, 5, 6],
        "p_malignant": [0.99, 0.01, 0.48, 0.80, 0.20, 0.70],
        "jaccard_top_k": [1.0, 1.0, 0.8, 0.1, 0.6, 0.9],
        "spearman_abs_all_features": [0.9, 0.9, 0.7, 0.2, 0.5, 0.8],
        "n_direction_disagreements": [0, 0, 0, 1, 3, 0],
    })
    cases = {c["case_type"]: c["patient_id"] for c in select_case_studies(summary)}
    assert cases == {"Clearly malignant": 1, "Clearly benign": 2, "Borderline": 3,
                     "Ranking divergence": 4, "Direction disagreement": 5}
    summary["n_direction_disagreements"] = 0
    last = select_case_studies(summary)[-1]
    assert last["found"] is False and last["patient_id"] is None


def test_lime_stability(data, model):
    split = data[3]
    stab = lime_stability(model, split.X_train, split.X_test.iloc[[0]], seeds=(0, 1), num_samples=500)
    assert 0.0 <= stab["mean_pairwise_jaccard_top_k"] <= 1.0


# ------------------------------------------------------------------ visualisation
def test_plot_creation(data, model, shap_test, tmp_path):
    split = data[3]
    lime_res = explain_patient_lime(model, split.X_train, split.X_test.iloc[[0]], num_samples=500)
    cmp = compare_explanations(lime_res.weights, pd.Series(shap_test.values[0], index=split.feature_names))
    m = evaluate_classifier(model, split.X_test, split.y_test)
    figs = {
        "cm": viz.plot_confusion_matrix(m["confusion_matrix"]),
        "roc": viz.plot_roc({"RF": (np.array([0, 0.1, 1]), np.array([0, 0.9, 1]), 0.95)}),
        "gauge": viz.plot_risk_gauge(0.7),
        "lime": viz.plot_lime(lime_res.table),
        "bar": viz.plot_shap_global_bar(global_importance(shap_test)),
        "bee": viz.plot_shap_beeswarm(shap_test),
        "waterfall": viz.plot_shap_waterfall(shap_test[0]),
        "force": viz.plot_shap_force_matplotlib(shap_test[0]),
        "cmp": viz.plot_lime_vs_shap(cmp["direction_table"]),
        "arch": viz.plot_architecture(),
    }
    for name, fig in figs.items():
        assert isinstance(fig, Figure), name
        viz.save(fig, tmp_path / f"{name}.png")
        assert (tmp_path / f"{name}.png").stat().st_size > 1000, name
        plt.close(fig)
    html = viz.shap_force_html(shap_test[0])
    assert "<script" in html.lower()


# ------------------------------------------------------------------ invalid input
@pytest.mark.parametrize("mutate, msg", [
    (lambda d: d.update({"mean radius": float("nan")}), "Non-finite"),
    (lambda d: d.update({"mean radius": float("inf")}), "Non-finite"),
    (lambda d: d.update({"mean radius": -1.0}), "Negative"),
    (lambda d: d.update({"mean radius": "abc"}), "numeric"),
    (lambda d: d.pop("mean radius"), "Missing"),
    (lambda d: d.update({"bogus feature": 1.0}), "Unknown"),
])
def test_invalid_numeric_input(data, mutate, msg):
    names, split = data[2], data[3]
    d = split.X_test.iloc[0].to_dict()
    mutate(d)
    with pytest.raises(ValueError, match=msg):
        validate_patient_input(d, names)


def test_invalid_input_length(data):
    with pytest.raises(ValueError, match="Expected 30"):
        validate_patient_input([1.0, 2.0], data[2])


# ------------------------------------------------------------------ application smoke test
def test_streamlit_app_runs_and_updates_on_patient_change():
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=300).run()
    assert not at.exception, [e.value for e in at.exception]
    assert [t.label for t in at.tabs] == ["Overview", "Diagnostic Prediction", "LIME Explanation",
                                          "SHAP Explanation", "LIME vs SHAP", "Model Evaluation", "Case Studies"]
    before = {m.label: m.value for m in at.metric}
    bundle = load_bundle()
    p = malignant_proba(bundle["model"], bundle["X_test"])
    current = at.selectbox(key="patient_id").value
    # switch to whichever extreme-probability patient is not currently selected
    lowest, highest = int(bundle["X_test"].index[np.argmin(p)]), int(bundle["X_test"].index[np.argmax(p)])
    at.selectbox(key="patient_id").set_value(lowest if current != lowest else highest).run()
    assert not at.exception
    after = {m.label: m.value for m in at.metric}
    assert before["Sum of SHAP values"] != after["Sum of SHAP values"] or \
        before["Local fit R²"] != after["Local fit R²"]
