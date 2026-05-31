import json
from pathlib import Path
from typing import Dict, Optional

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from src.config import (
    CUSTOMER_ID_COLUMN,
    MODELS_DIR,
    RANDOM_STATE,
    TRAINING_REPORTS_DIR,
    TARGET_COLUMN,
    TEST_SIZE,
)


def prepare_features_and_target(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Prepares feature matrix X and target vector y for churn prediction.
    """
    model_df = df.copy()

    columns_to_drop = []

    if CUSTOMER_ID_COLUMN in model_df.columns:
        columns_to_drop.append(CUSTOMER_ID_COLUMN)

    if "ingestion_date" in model_df.columns:
        columns_to_drop.append("ingestion_date")

    model_df = model_df.drop(columns=columns_to_drop)

    y = model_df[TARGET_COLUMN].map({"No": 0, "Yes": 1})
    X = model_df.drop(columns=[TARGET_COLUMN])

    X = pd.get_dummies(X, drop_first=True)

    return X, y


def build_model_path(source_file: Optional[Path] = None) -> Path:
    """
    Builds a versioned model path inside models/.

    Example:
        customer_churn_2026_05_29.csv
        -> models/customer_churn_2026_05_29_model.pkl
    """
    if source_file is None:
        return MODELS_DIR / "churn_model.pkl"

    return MODELS_DIR / f"{source_file.stem}_model.pkl"


def build_metrics_path(source_file: Optional[Path] = None) -> Path:
    """
    Builds a metrics output path inside reports/training/.
    """
    if source_file is None:
        return TRAINING_REPORTS_DIR / "training_metrics.json"

    return TRAINING_REPORTS_DIR / f"{source_file.stem}_training_metrics.json"


def save_training_metrics(
    metrics: Dict[str, float],
    source_file: Optional[Path] = None,
) -> None:
    """
    Saves model evaluation metrics as JSON.
    """
    metrics_path = build_metrics_path(source_file)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)

    with open(metrics_path, "w") as file:
        json.dump(metrics, file, indent=4)

    print(f"[TRAINING] Metrics saved to: {metrics_path}")


def train_churn_model(
    df: pd.DataFrame,
    source_file: Optional[Path] = None,
) -> Dict[str, float]:
    """
    Trains a Random Forest churn model and saves a versioned model artifact.
    """
    X, y = prepare_features_and_target(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=RANDOM_STATE,
        class_weight="balanced",
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    model_path = build_model_path(source_file)

    metrics = {
        "source_file": str(source_file) if source_file else None,
        "model_path": str(model_path),
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "feature_count": int(X.shape[1]),
    }

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)

    print(f"[TRAINING] Model saved to: {model_path}")
    print(f"[TRAINING] Metrics: {metrics}")

    save_training_metrics(metrics, source_file)

    return metrics