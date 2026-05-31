from pathlib import Path
from typing import Tuple, Optional
import pandas as pd
from src.config import RAW_DATA_DIR

def get_latest_csv_file(raw_data_dir: Path= RAW_DATA_DIR) -> Path:
    """
    To find the most recently modified data file
    """

    csv_files = list(raw_data_dir.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(f"No csv files found in {raw_data_dir}")
    
    latest_file = max(csv_files, key=lambda file: file.stat().st_mtime)
    return latest_file

def load_raw_data(input_file: Optional[str] = None) -> Tuple[pd.DataFrame,Path]:
    """
    Loads either the latest csv file or any specific one if path is given
    """
    if input_file:
        selected_file =RAW_DATA_DIR/input_file
        if not selected_file.exists():
            raise FileNotFoundError(f"The file with path: {selected_file}")
        
        if selected_file.suffix.lower() != ".csv":
            raise ValueError(f"Inpur file must be a csv file: {selected_file}")
    else:
        selected_file = get_latest_csv_file()

        df = pd.read_csv( selected_file)

        print(f"[ingestion] Loaded raw data from the path {selected_file}")
        print(f"[ingestion] Raw data shape: {df.shape}")

        return df, selected_file