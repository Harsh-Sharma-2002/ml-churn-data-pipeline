from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR= PROJECT_ROOT/"data"/"raw"
SOURCE_FILE_NAME = "customer_churn_full.csv"

DAY_1_FILE="customer_churn_2026_05_29.csv"
DAY_2_FILE="customer_churn_2026_05_30.csv"
DAY_3_FILE="customer_churn_2026_05_31.csv"

def load_source_data() -> pd.DataFrame:
    source_path = RAW_DATA_DIR/SOURCE_FILE_NAME

    if not source_path.exists():
        raise FileNotFoundError(f"file with name {source_path} not found")
    df = pd.read_csv(source_path)
    print(f"demo data created with source file: {source_path} with shape of {df.shape}")

    return df



def split_into_daily_files(df:pd.DataFrame) -> None:
    """
    Splits data frame into daily based data files 
    """

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    day_1_df = df.iloc[:2500].copy()
    day_2_df = df.iloc[2500:5000].copy()
    day_3_df = df.iloc[5000:].copy()

    day_1_path = RAW_DATA_DIR / DAY_1_FILE
    day_2_path = RAW_DATA_DIR / DAY_2_FILE
    day_3_path = RAW_DATA_DIR / DAY_3_FILE

    day_1_df.to_csv(day_1_path, index=False)
    day_2_df.to_csv(day_2_path, index=False)
    day_3_df.to_csv(day_3_path, index=False)

    print(f"Created valid Day 1 file: {day_1_path} | shape={day_1_df.shape}")
    print(f"Created Day 2 file before corruption: {day_2_path} | shape={day_2_df.shape}")
    print(f"Created valid Day 3 file: {day_3_path} | shape={day_3_df.shape}")

def corrupt_day_2_file() -> None:
    """
    intentionally curruptind day 2 file to to test validation logic 
    """

    day_2_path = RAW_DATA_DIR/DAY_2_FILE

    if not day_2_path.exists():
        raise FileNotFoundError(f"File with path: {day_2_path}  not found")
    
    df = pd.read_csv(day_2_path)

    df.loc[df.index[:10], "MonthlyCharges"] = -999
    df.loc[df.index[10:20], "tenure"] = -5
    df = df.drop(columns=["Churn"])

    df.to_csv(day_2_path, index=False)

    print(f"Corrupted Day 2 file: {day_2_path}")
    print("Corruptions applied:")
    print("  - Dropped required target column: Churn")
    print("  - Added negative MonthlyCharges values")
    print("  - Added negative tenure values")

def main() -> None:
    df = load_source_data()
    split_into_daily_files(df)
    corrupt_day_2_file()

    print("[DEMO DATA] Demo data preparation complete.")


if __name__ == "__main__":
    main()