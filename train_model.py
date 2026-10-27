"""Train the ClinXAI Random Forest (and a Logistic Regression baseline), evaluate on the held-out
test set, and save the model bundle plus report-ready metrics and figures.

Usage:  python train_model.py
"""
import json

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from src.config import FIGURES_DIR, METRICS_DIR, MODEL_PATH, RF_PARAMS, ensure_dirs
from src.data_loader import dataset_overview, load_dataset, split_data
from src.model import (
    cross_validated_auc,
    evaluate_classifier,
    roc_points,
    save_bundle,
    train_logistic_baseline,
    train_random_forest,
)
from src.visualization import plot_confusion_matrix, plot_roc, save


def main() -> dict:
    ensure_dirs()
    X, y, feature_names = load_dataset()
    split = split_data(X, y)
    print(f"Dataset: {X.shape[0]} samples x {X.shape[1]} features | malignant (1) = {int(y.sum())}, "
          f"benign (0) = {int((y == 0).sum())}")
    print(f"Train: {len(split.X_train)} | Test: {len(split.X_test)} (stratified, random_state=42)")

    rf = train_random_forest(split.X_train, split.y_train)
    lr = train_logistic_baseline(split.X_train, split.y_train)

    rf_metrics = evaluate_classifier(rf, split.X_test, split.y_test)
    lr_metrics = evaluate_classifier(lr, split.X_test, split.y_test)
    rf_metrics.update(cross_validated_auc(lambda: RandomForestClassifier(**RF_PARAMS),
                                          split.X_train, split.y_train))

    metrics = {
        "dataset": {
            "name": "Breast Cancer Wisconsin (Diagnostic) — sklearn.datasets.load_breast_cancer",
            "n_samples": int(X.shape[0]),
            "n_features": int(X.shape[1]),
            "label_encoding": {"malignant": 1, "benign": 0},
            "n_malignant": int(y.sum()),
            "n_benign": int((y == 0).sum()),
            "n_train": len(split.X_train),
            "n_test": len(split.X_test),
            "test_malignant": int(split.y_test.sum()),
            "test_benign": int((split.y_test == 0).sum()),
            "split": "stratified 80/20, random_state=42",
        },
        "random_forest": {"params": {k: v for k, v in RF_PARAMS.items()}, **rf_metrics},
        "logistic_regression_baseline": lr_metrics,
    }

    save_bundle(rf, lr, split, metrics)
    with open(METRICS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    rows = []
    for name, m in [("Random Forest", rf_metrics), ("Logistic Regression (baseline)", lr_metrics)]:
        rows.append({"model": name, **{k: m[k] for k in
                     ["accuracy", "precision", "recall_sensitivity", "specificity", "f1", "roc_auc"]},
                     **m["confusion_matrix"]})
    pd.DataFrame(rows).round(4).to_csv(METRICS_DIR / "metrics.csv", index=False)
    dataset_overview(X, y).to_csv(METRICS_DIR / "dataset_overview.csv")

    save(plot_confusion_matrix(rf_metrics["confusion_matrix"], "Random Forest — confusion matrix (test set)"),
         FIGURES_DIR / "confusion_matrix.png")
    curves = {
        "Random Forest": (*roc_points(rf, split.X_test, split.y_test), rf_metrics["roc_auc"]),
        "Logistic Regression": (*roc_points(lr, split.X_test, split.y_test), lr_metrics["roc_auc"]),
    }
    save(plot_roc(curves), FIGURES_DIR / "roc_curve.png")
    plt.close("all")

    print("\nTest-set metrics (positive class = Malignant):")
    print(pd.DataFrame(rows).set_index("model").round(4).to_string())
    print(f"\nRF 5-fold CV ROC-AUC on training set: {rf_metrics['cv_roc_auc_mean']:.4f} "
          f"+/- {rf_metrics['cv_roc_auc_std']:.4f}")
    print(f"\nSaved model bundle -> {MODEL_PATH}")
    return metrics


if __name__ == "__main__":
    main()
