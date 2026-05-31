import json
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from src.config import (
    REQUIRED_COLUMNS,
    TARGET_COLUMN,
    VALID_CHURN_VALUES,
    MINIMUM_ROW_COUNT,
    PRE_CLEAN_REPORTS_DIR,
    POST_CLEAN_REPORTS_DIR,
    COMBINED_REPORTS_DIR,
)


def get_file_stem(source_file: Optional[Path]) -> str:
    """
    Returns a safe file stem for naming validation reports.

    Example:
        data/raw/customer_churn_2026_05_29.csv
        -> customer_churn_2026_05_29
    """
    if source_file is None:
        return "unknown_source"

    return source_file.stem


def save_json_report(report: Dict[str, Any], output_path: Path) -> None:
    """
    Saves a dictionary report as a JSON file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as file:
        json.dump(report, file, indent=4)

    print(f"[VALIDATION] Report saved to: {output_path}")


def validate_raw_schema(
    df: pd.DataFrame,
    source_file: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Performs pre-clean validation on the raw dataframe.

    This checks whether the raw CSV is structurally usable before the
    pipeline spends time cleaning or training.

    Checks:
    - Dataset is not empty
    - Required columns exist
    - Target column exists
    - Target column is not completely missing
    - Target values are recognizable as Yes/No
    """
    checks = {}

    checks["not_empty"] = bool(not df.empty)

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]
    checks["required_columns_exist"] = bool(len(missing_columns) == 0)

    checks["target_column_exists"] = bool(TARGET_COLUMN in df.columns)

    if checks["target_column_exists"]:
        target_series = df[TARGET_COLUMN]

        checks["target_not_all_missing"] = bool(not target_series.isna().all())

        raw_target_values = set(
            target_series
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
        )

        invalid_target_values = sorted(
            list(raw_target_values - VALID_CHURN_VALUES)
        )

        checks["target_values_recognizable"] = bool(
            len(invalid_target_values) == 0
        )
    else:
        invalid_target_values = []
        checks["target_not_all_missing"] = False
        checks["target_values_recognizable"] = False

    passed = bool(all(checks.values()))
    file_stem = get_file_stem(source_file)

    report = {
        "source_file": str(source_file) if source_file else None,
        "validation_stage": "pre_clean_raw_schema_validation",
        "passed": passed,
        "checks": checks,
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "missing_columns": missing_columns,
        "invalid_target_values": invalid_target_values,
    }

    output_path = PRE_CLEAN_REPORTS_DIR / f"{file_stem}_raw_validation.json"
    save_json_report(report, output_path)

    if passed:
        print("[VALIDATION] Pre-clean raw schema validation passed.")
    else:
        print("[VALIDATION] Pre-clean raw schema validation failed.")
        print(f"[VALIDATION] Missing columns: {missing_columns}")
        print(f"[VALIDATION] Invalid target values: {invalid_target_values}")

    return report


def validate_clean_data(
    df: pd.DataFrame,
    source_file: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Performs post-clean validation on the cleaned dataframe.

    This is the final data-quality gate before model training.

    Checks:
    - Dataset is not empty after cleaning
    - Dataset has minimum required row count
    - Target column exists
    - Target column has no missing values
    - Target contains only Yes/No
    - Target has at least two classes
    - tenure is numeric and non-negative
    - MonthlyCharges is numeric and non-negative
    - TotalCharges is numeric and non-negative
    """
    checks = {}

    checks["not_empty_after_cleaning"] = bool(not df.empty)
    checks["minimum_row_count"] = bool(len(df) >= MINIMUM_ROW_COUNT)
    checks["target_column_exists"] = bool(TARGET_COLUMN in df.columns)

    if checks["target_column_exists"]:
        target_series = df[TARGET_COLUMN]

        checks["target_has_no_missing_values"] = bool(
            not target_series.isna().any()
        )

        target_values = set(
            target_series
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
        )

        invalid_target_values = sorted(
            list(target_values - VALID_CHURN_VALUES)
        )

        checks["target_values_valid"] = bool(len(invalid_target_values) == 0)
        checks["target_has_two_classes"] = bool(len(target_values) >= 2)
    else:
        invalid_target_values = []
        checks["target_has_no_missing_values"] = False
        checks["target_values_valid"] = False
        checks["target_has_two_classes"] = False

    numeric_columns = ["tenure", "MonthlyCharges", "TotalCharges"]
    numeric_column_issues = {}

    for column in numeric_columns:
        if column not in df.columns:
            checks[f"{column}_exists"] = False
            checks[f"{column}_numeric"] = False
            checks[f"{column}_non_negative"] = False
            numeric_column_issues[column] = "missing_column"
            continue

        numeric_series = pd.to_numeric(df[column], errors="coerce")

        checks[f"{column}_exists"] = True
        checks[f"{column}_numeric"] = bool(not numeric_series.isna().any())
        checks[f"{column}_non_negative"] = bool((numeric_series >= 0).all())

        if numeric_series.isna().any():
            numeric_column_issues[column] = (
                "contains_non_numeric_or_missing_values"
            )
        elif not (numeric_series >= 0).all():
            numeric_column_issues[column] = "contains_negative_values"

    passed = bool(all(checks.values()))
    file_stem = get_file_stem(source_file)

    report = {
        "source_file": str(source_file) if source_file else None,
        "validation_stage": "post_clean_validation",
        "passed": passed,
        "checks": checks,
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "invalid_target_values": invalid_target_values,
        "numeric_column_issues": numeric_column_issues,
    }

    output_path = POST_CLEAN_REPORTS_DIR / f"{file_stem}_post_clean_validation.json"
    save_json_report(report, output_path)

    if passed:
        print("[VALIDATION] Post-clean validation passed.")
    else:
        print("[VALIDATION] Post-clean validation failed.")
        print(f"[VALIDATION] Invalid target values: {invalid_target_values}")
        print(f"[VALIDATION] Numeric column issues: {numeric_column_issues}")

    return report


def save_combined_validation_report(
    pre_clean_report: Dict[str, Any],
    post_clean_report: Optional[Dict[str, Any]],
    source_file: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Saves a combined validation summary for one pipeline run.

    If pre-clean validation fails, post_clean_report can be None.
    """
    file_stem = get_file_stem(source_file)

    overall_passed = bool(
        pre_clean_report.get("passed", False)
        and post_clean_report is not None
        and post_clean_report.get("passed", False)
    )

    combined_report = {
        "source_file": str(source_file) if source_file else None,
        "overall_passed": overall_passed,
        "pre_clean_validation": pre_clean_report,
        "post_clean_validation": post_clean_report,
    }

    output_path = COMBINED_REPORTS_DIR / f"{file_stem}_validation_summary.json"
    save_json_report(combined_report, output_path)

    if overall_passed:
        print("[VALIDATION] Combined validation passed.")
    else:
        print("[VALIDATION] Combined validation failed.")

    return combined_report