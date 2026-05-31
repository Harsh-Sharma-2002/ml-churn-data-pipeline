from typing import Optional

from prefect import flow, task

from src.pipeline import run_pipeline


@task(name="Run churn ETL validation and training pipeline")
def run_pipeline_task(input_file: Optional[str] = None) -> dict:
    """
    Runs one pipeline attempt.

    If no unprocessed CSV exists, the pipeline returns no_new_data.
    """
    return run_pipeline(input_file=input_file)


@flow(name="daily-churn-ml-pipeline")
def churn_pipeline_flow(input_file: Optional[str] = None) -> dict:
    """
    Prefect flow for the churn ML data pipeline.

    taking 20 sec day for simulation
    """
    result = run_pipeline_task(input_file=input_file)
    return result


if __name__ == "__main__":
    churn_pipeline_flow.serve(
        name="churn-pipeline-20-second-demo-schedule",
        interval=20, # 86400 for day
    )