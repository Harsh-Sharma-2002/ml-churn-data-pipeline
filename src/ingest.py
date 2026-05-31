from pathlib import Path
from typing import Optional, Tuple

import pandas as pd

from src.config import RAW_DATA_DIR
from src.state import get_processed_file_names


def get_next_unprocessed_csv_file(raw_data_dir: Path = RAW_DATA_DIR) -> Optional[Path]:
    """
    Finds the next unprocessed CSV file in data/raw/.

    Files are sorted by filename so customer_churn_2026_05_29.csv
    is processed before customer_churn_2026_05_30.csv.
    """
    csv_files = sorted(raw_data_dir.glob("*.csv"), key=lambda file: file.name)

    if not csv_files:
        return None

    processed_file_names = get_processed_file_names()

    for csv_file in csv_files:
        if csv_file.name not in processed_file_names:
            return csv_file

    return None


def get_csv_file_by_name(input_file: str, raw_data_dir: Path = RAW_DATA_DIR) -> Path:
    """
    Gets a specific CSV file from data/raw/.
    """
    selected_file = raw_data_dir / input_file

    if not selected_file.exists():
        raise FileNotFoundError(f"CSV file not found: {selected_file}")

    if selected_file.suffix.lower() != ".csv":
        raise ValueError(f"Input file must be a CSV file: {selected_file}")

    return selected_file


def load_raw_data(input_file: Optional[str] = None) -> Tuple[Optional[pd.DataFrame], Optional[Path]]:
    """
    Loads either:
    - a specific CSV file from data/raw/, or
    - the next unprocessed CSV file from data/raw/.

    Returns (None, None) when no unprocessed file is available.
    """
    if input_file:
        selected_file = get_csv_file_by_name(input_file)
    else:
        selected_file = get_next_unprocessed_csv_file()

    if selected_file is None:
        print("[INGESTION] No new unprocessed CSV files found in data/raw/.")
        return None, None

    df = pd.read_csv(selected_file)

    print(f"[INGESTION] Loaded raw data from: {selected_file}")
    print(f"[INGESTION] Raw data shape: {df.shape}")

    return df, selected_file