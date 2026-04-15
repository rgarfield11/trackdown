import subprocess
import os
from pathlib import Path

from prefect import flow, task, get_run_logger

from extract import main as extract_main
from load import main as load_main

DBT_DIR = Path(__file__).parent.parent / "dbt"


@task(name="extract")
def extract():
    logger = get_run_logger()
    logger.info("Extracting tracks from Deezer...")
    extract_main()


@task(name="load")
def load():
    logger = get_run_logger()
    logger.info("Loading tracks into Snowflake...")
    load_main()


@task(name="dbt_run")
def dbt_run():
    logger = get_run_logger()
    logger.info("Running dbt models...")
    result = subprocess.run(
        ["dbt", "run"],
        cwd=DBT_DIR,
        capture_output=True,
        text=True,
    )
    logger.info(result.stdout)
    if result.returncode != 0:
        logger.error(result.stderr)
        raise RuntimeError("dbt run failed")


@flow(name="trackdown-pipeline")
def pipeline():
    extract()
    load()
    dbt_run()


if __name__ == "__main__":
    pipeline()
