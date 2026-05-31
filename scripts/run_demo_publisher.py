import shutil
import time
from pathlib import Path

from src.config import DEMO_DAILY_FILES_DIR, DEMO_FILES, RAW_DATA_DIR


def publish_file(file_name: str) -> Path:
    """
    Copies one staged daily CSV into the raw ingestion directory.
    """
    source_path = DEMO_DAILY_FILES_DIR / file_name
    destination_path = RAW_DATA_DIR / file_name

    if not source_path.exists():
        raise FileNotFoundError(
            f"Demo file not found: {source_path}. "
            "Run python -m scripts.prepare_demo_data first."
        )

    shutil.copy2(source_path, destination_path)

    print(f"[DEMO PUBLISHER] Published daily CSV: {destination_path}")

    return destination_path


def run_publisher(wait_seconds: int = 20) -> None:
    """
    Simulates daily CSV arrivals.

    Every 20 seconds, a new CSV lands in data/raw/.
    Prefect is responsible for detecting and running the pipeline.
    """
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, file_name in enumerate(DEMO_FILES):
        print("=" * 80)
        print(f"[DEMO PUBLISHER] Simulated day {index + 1}: publishing {file_name}")

        publish_file(file_name)

        if index < len(DEMO_FILES) - 1:
            print(f"[DEMO PUBLISHER] Waiting {wait_seconds} seconds before publishing next file...")
            time.sleep(wait_seconds)

    print("=" * 80)
    print("[DEMO PUBLISHER] Finished publishing demo files.")


if __name__ == "__main__":
    run_publisher(wait_seconds=20)