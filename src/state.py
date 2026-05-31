import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from src.config import PROCESSED_MANIFEST_PATH


def load_processed_manifest() -> Dict[str, List[dict]]:
    """
    Loads the manifest of files already handled by the pipeline.
    """
    if not PROCESSED_MANIFEST_PATH.exists():
        return {"processed_files": []}

    with open(PROCESSED_MANIFEST_PATH, "r") as file:
        return json.load(file)


def get_processed_file_names() -> set[str]:
    """
    Returns names of files already handled by the pipeline.
    """
    manifest = load_processed_manifest()

    return {
        item["file_name"]
        for item in manifest.get("processed_files", [])
    }


def mark_file_as_processed(
    source_file: Path,
    status: str,
    training_triggered: bool,
) -> None:
    """
    Marks a raw CSV file as handled so scheduled Prefect runs do not process it again.
    """
    PROCESSED_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

    manifest = load_processed_manifest()

    processed_files = manifest.get("processed_files", [])

    processed_files.append(
        {
            "file_name": source_file.name,
            "file_path": str(source_file),
            "status": status,
            "training_triggered": training_triggered,
            "processed_at_utc": datetime.now(timezone.utc).isoformat(),
        }
    )

    manifest["processed_files"] = processed_files

    with open(PROCESSED_MANIFEST_PATH, "w") as file:
        json.dump(manifest, file, indent=4)

    print(f"[STATE] Marked file as processed: {source_file.name}")