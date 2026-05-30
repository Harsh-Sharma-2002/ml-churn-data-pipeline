from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REJECTED_DATA_DIR = DATA_DIR / "rejected"

MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
LOGS_DIR = PROJECT_ROOT / "logs"

PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "processed_churn.csv"
REJECTED_DATA_PATH = REJECTED_DATA_DIR / "rejected_churn.csv"
VALIDATION_REPORT_PATH = REPORTS_DIR / "validation_report.json"
TRAINING_METRICS_PATH = REPORTS_DIR / "training_metrics.json"
MODEL_PATH = MODELS_DIR / "churn_model.pkl"

TARGET_COLUMN = "Churn"
CUSTOMER_ID_COLUMN = "customerID"
MINIMUM_ROW_COUNT = 100
RANDOM_STATE = 42
TEST_SIZE = 0.2

REQUIRED_COLUMNS = [
    "customerID",
    "gender",
    "SeniorCitizen",
    "Partner",
    "Dependents",
    "tenure",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
    "MonthlyCharges",
    "TotalCharges",
    "Churn",
]

# Valid target values
VALID_CHURN_VALUES = {"Yes", "No"}