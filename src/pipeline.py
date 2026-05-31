import argparse
from pathlib import Path
from typing import Optional

from src.clean import clean_churn_data
from src.config import PROCESSED_DATA_DIR, REJECTED_DATA_DIR
from src.ingest import load_raw_data
from src.state import mark_file_as_processed
from src.train import train_churn_model
from src.validate import (
    save_combined_validation_report,
    validate_clean_data,
    validate_raw_schema,
)


def build_output_path(output_dir: Path, source_file: Path, suffix: str) -> Path:
    """
    Builds an output path based on the input file name.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    return output_dir / f"{source_file.stem}_{suffix}.csv"


def run_pipeline(input_file: Optional[str] = None) -> dict:
    """
    Runs the full churn ETL + validation + conditional training pipeline.
    """
    print("[PIPELINE] Starting churn ML data pipeline.")

    raw_df, source_file = load_raw_data(input_file)

    if raw_df is None or source_file is None:
        print("[PIPELINE] No new data to process.")
        return {
            "status": "no_new_data",
            "source_file": None,
            "training_triggered": False,
        }

    pre_clean_report = validate_raw_schema(raw_df, source_file)

    if not pre_clean_report["passed"]:
        rejected_path = build_output_path(
            REJECTED_DATA_DIR,
            source_file,
            "raw_rejected",
        )
        raw_df.to_csv(rejected_path, index=False)

        combined_report = save_combined_validation_report(
            pre_clean_report,
            post_clean_report=None,
            source_file=source_file,
        )

        mark_file_as_processed(
            source_file=source_file,
            status="failed_pre_clean_validation",
            training_triggered=False,
        )

        print(f"[PIPELINE] Pre-clean validation failed. Rejected data saved to: {rejected_path}")
        print("[PIPELINE] Training skipped.")

        return {
            "status": "failed_pre_clean_validation",
            "source_file": str(source_file),
            "rejected_data_path": str(rejected_path),
            "combined_validation": combined_report,
            "training_triggered": False,
        }

    clean_df = clean_churn_data(raw_df)

    post_clean_report = validate_clean_data(clean_df, source_file)

    combined_report = save_combined_validation_report(
        pre_clean_report,
        post_clean_report,
        source_file,
    )

    if not post_clean_report["passed"]:
        rejected_path = build_output_path(
            REJECTED_DATA_DIR,
            source_file,
            "cleaned_rejected",
        )
        clean_df.to_csv(rejected_path, index=False)

        mark_file_as_processed(
            source_file=source_file,
            status="failed_post_clean_validation",
            training_triggered=False,
        )

        print(f"[PIPELINE] Post-clean validation failed. Rejected data saved to: {rejected_path}")
        print("[PIPELINE] Training skipped.")

        return {
            "status": "failed_post_clean_validation",
            "source_file": str(source_file),
            "rejected_data_path": str(rejected_path),
            "combined_validation": combined_report,
            "training_triggered": False,
        }

    processed_path = build_output_path(
        PROCESSED_DATA_DIR,
        source_file,
        "processed",
    )
    clean_df.to_csv(processed_path, index=False)

    print(f"[PIPELINE] Processed data saved to: {processed_path}")
    print("[PIPELINE] Validation passed. Triggering model training.")

    metrics = train_churn_model(clean_df, source_file)

    mark_file_as_processed(
        source_file=source_file,
        status="success",
        training_triggered=True,
    )

    print("[PIPELINE] Pipeline completed successfully.")

    return {
        "status": "success",
        "source_file": str(source_file),
        "processed_data_path": str(processed_path),
        "combined_validation": combined_report,
        "training_triggered": True,
        "training_metrics": metrics,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the churn ML data pipeline."
    )

    parser.add_argument(
        "--input-file",
        type=str,
        default=None,
        help="Optional CSV file name inside data/raw/. If omitted, next unprocessed CSV is used.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(input_file=args.input_file)