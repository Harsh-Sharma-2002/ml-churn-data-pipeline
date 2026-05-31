from datetime import date

import pandas as pd

def clean_churn_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw customer chutn data

    - Copy df to not mutate the orignal
    - Strip whitesdpsaces from strs
    - Remove duplicate rows
    - Convert total charges to numeric
    - Drop rows with missing total charges
    - Add ingestion date fro tracking
    """

    clean_df = df.copy()

    #############################

    string_cols = clean_df.select_dtypes(include=["object"]).columns

    for cols in string_cols:
        clean_df[cols] = clean_df[cols].astype(str).str.strip() 

    #############################

    before_dedup = len(clean_df)
    clean_df = clean_df.drop_duplicates()
    after_dedup = len(clean_df)

    removed_duplicates = before_dedup - after_dedup

    #############################

    if "TotalCharges" in clean_df.columns:
        clean_df["TotalCharges"] = pd.to_numeric(
                                                clean_df["TotalCharges"],
                                                 errors="coerce"
                                                 )
        before_drop = len(clean_df)
        clean_df = clean_df.dropna(subset=["TotalCharges"])
        after_drop = len(clean_df)


        removed_missing_total = before_drop - after_drop
    else:
        removed_missing_total = 0


   #############################
   #      
    clean_df["ingestion_date"] = date.today().isoformat()

    print(f"[CLEANING] Removed duplicate rows: {removed_duplicates}")
    print(f"[CLEANING] Removed rows with missing TotalCharges: {removed_missing_total}")
    print(f"[CLEANING] Cleaned data shape: {clean_df.shape}")

    return clean_df
    

