from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
DEMO_DAILY_FILES_DIR = DATA_DIR / "demo_daily_files"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REJECTED_DATA_DIR = DATA_DIR / "rejected"

MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
LOGS_DIR = PROJECT_ROOT / "logs"

PRE_CLEAN_REPORTS_DIR = REPORTS_DIR / "pre_clean"
POST_CLEAN_REPORTS_DIR = REPORTS_DIR / "post_clean"
COMBINED_REPORTS_DIR = REPORTS_DIR / "combined"
TRAINING_REPORTS_DIR = REPORTS_DIR / "training"

SOURCE_DATA_PATH = PROJECT_ROOT / "customer_churn_full.csv"
PROCESSED_MANIFEST_PATH = LOGS_DIR / "processed_files.json"

MODEL_PATH = MODELS_DIR / "churn_model.pkl"

TARGET_COLUMN = "Churn"
CUSTOMER_ID_COLUMN = "customerID"
MINIMUM_ROW_COUNT = 100
RANDOM_STATE = 42
TEST_SIZE = 0.2

DAY_1_FILE = "customer_churn_2026_05_29.csv"
DAY_2_FILE = "customer_churn_2026_05_30.csv"
DAY_3_FILE = "customer_churn_2026_05_31.csv"

DEMO_FILES = [
    DAY_1_FILE,
    DAY_2_FILE,
    DAY_3_FILE,
]

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

VALID_CHURN_VALUES = {"Yes", "No"}