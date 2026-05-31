import pandas as pd

from src.config import (
    DAY_1_FILE,
    DAY_2_FILE,
    DAY_3_FILE,
    DEMO_DAILY_FILES_DIR,
    RAW_DATA_DIR,
    SOURCE_DATA_PATH,
)


def load_source_data() -> pd.DataFrame:
    if not SOURCE_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Source file not found: {SOURCE_DATA_PATH}. "
            "Expected customer_churn_full.csv in the project root."
        )

    df = pd.read_csv(SOURCE_DATA_PATH)

    print(f"[DEMO DATA] Loaded source file: {SOURCE_DATA_PATH}")
    print(f"[DEMO DATA] Source shape: {df.shape}")

    return df


def clear_demo_dirs() -> None:
    """
    Clears generated demo files and active raw files.
    """
    DEMO_DAILY_FILES_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for csv_file in DEMO_DAILY_FILES_DIR.glob("*.csv"):
        csv_file.unlink()

    for csv_file in RAW_DATA_DIR.glob("*.csv"):
        csv_file.unlink()

    print("[DEMO DATA] Cleared data/demo_daily_files/ and data/raw/ CSV files.")


def split_into_daily_files(df: pd.DataFrame) -> None:
    """
    Splits the source dataframe into three staged daily files.
    """
    day_1_df = df.iloc[:2500].copy()
    day_2_df = df.iloc[2500:5000].copy()
    day_3_df = df.iloc[5000:].copy()

    day_1_df.to_csv(DEMO_DAILY_FILES_DIR / DAY_1_FILE, index=False)
    day_2_df.to_csv(DEMO_DAILY_FILES_DIR / DAY_2_FILE, index=False)
    day_3_df.to_csv(DEMO_DAILY_FILES_DIR / DAY_3_FILE, index=False)

    print(f"[DEMO DATA] Created valid Day 1 file: {DAY_1_FILE}")
    print(f"[DEMO DATA] Created Day 2 file before corruption: {DAY_2_FILE}")
    print(f"[DEMO DATA] Created valid Day 3 file: {DAY_3_FILE}")


def corrupt_day_2_file() -> None:
    """
    Intentionally corrupts Day 2 to test validation failure.
    """
    day_2_path = DEMO_DAILY_FILES_DIR / DAY_2_FILE

    if not day_2_path.exists():
        raise FileNotFoundError(f"Day 2 file not found: {day_2_path}")

    df = pd.read_csv(day_2_path)

    if "MonthlyCharges" in df.columns:
        df.loc[df.index[:10], "MonthlyCharges"] = -999

    if "tenure" in df.columns:
        df.loc[df.index[10:20], "tenure"] = -5

    if "Churn" in df.columns:
        df = df.drop(columns=["Churn"])

    df.to_csv(day_2_path, index=False)

    print("[DEMO DATA] Corrupted Day 2 file:")
    print("  - Dropped required target column: Churn")
    print("  - Added negative MonthlyCharges values")
    print("  - Added negative tenure values")


def main() -> None:
    clear_demo_dirs()
    df = load_source_data()
    split_into_daily_files(df)
    corrupt_day_2_file()

    print("[DEMO DATA] Demo data preparation complete.")


if __name__ == "__main__":
    main()