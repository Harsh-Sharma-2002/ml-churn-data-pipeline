from typing import Optional

from prefect import flow, task

from src.pipeline import run_pipeline


@task(name="Run churn ETL validation and training pipeline")
def run_pipeline_task(input_file: Optional[str] = None) -> dict:
    """
    Runs the full churn data pipeline as a Prefect task.
    """
    return run_pipeline(input_file=input_file)


@flow(name="daily-churn-ml-pipeline")
def churn_pipeline_flow(input_file: Optional[str] = None) -> dict:
    """
    Prefect flow for the churn ML data pipeline.

    The flow can be run manually for a specific file, or scheduled daily
    to automatically ingest the latest CSV from data/raw/.
    """
    result = run_pipeline_task(input_file=input_file)
    return result


if __name__ == "__main__":
    # Manual run for local development.
    # If input_file=None, the pipeline picks the latest CSV from data/raw/.
    churn_pipeline_flow()