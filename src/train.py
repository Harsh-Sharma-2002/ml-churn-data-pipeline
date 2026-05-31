import json
from typing import Dict

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from src.config import (
    CUSTOMER_ID_COLUMN,
    MODEL_PATH,
    RANDOM_STATE,
    TARGET_COLUMN,
    TEST_SIZE,
    TRAINING_METRICS_PATH,
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


def save_training_metrics(metrics: Dict[str, float]) -> None:
    """
    Saves model evaluation metrics as JSON.
    """
    TRAINING_METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(TRAINING_METRICS_PATH, "w") as file:
        json.dump(metrics, file, indent=4)

    print(f"[TRAINING] Metrics saved to: {TRAINING_METRICS_PATH}")


def train_churn_model(df: pd.DataFrame) -> Dict[str, float]:
    """
    Trains a Random Forest churn model and saves the trained model.
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

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred)), 4),
        "recall": round(float(recall_score(y_test, y_pred)), 4),
        "f1_score": round(float(f1_score(y_test, y_pred)), 4),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "feature_count": int(X.shape[1]),
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print(f"[TRAINING] Model saved to: {MODEL_PATH}")
    print(f"[TRAINING] Metrics: {metrics}")

    save_training_metrics(metrics)

    return metrics