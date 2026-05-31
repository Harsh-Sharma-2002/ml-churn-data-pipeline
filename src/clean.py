from datetime import date

import pandas as pd


def clean_churn_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw customer churn data.

    Cleaning steps:
    - Copy dataframe to avoid mutating raw input
    - Strip whitespace from string columns
    - Remove duplicate rows
    - Convert TotalCharges to numeric
    - Drop rows with missing TotalCharges
    - Add ingestion_date for tracking
    """
    clean_df = df.copy()

    string_columns = clean_df.select_dtypes(include=["object"]).columns

    for column in string_columns:
        clean_df[column] = clean_df[column].astype(str).str.strip()

    before_dedup = len(clean_df)
    clean_df = clean_df.drop_duplicates()
    after_dedup = len(clean_df)

    removed_duplicates = before_dedup - after_dedup

    if "TotalCharges" in clean_df.columns:
        clean_df["TotalCharges"] = pd.to_numeric(
            clean_df["TotalCharges"],
            errors="coerce",
        )

        before_drop = len(clean_df)
        clean_df = clean_df.dropna(subset=["TotalCharges"])
        after_drop = len(clean_df)

        removed_missing_total = before_drop - after_drop
    else:
        removed_missing_total = 0

    clean_df["ingestion_date"] = date.today().isoformat()

    print(f"[CLEANING] Removed duplicate rows: {removed_duplicates}")
    print(f"[CLEANING] Removed rows with missing TotalCharges: {removed_missing_total}")
    print(f"[CLEANING] Cleaned data shape: {clean_df.shape}")

    return clean_df