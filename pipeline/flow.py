import subprocess
import os
from pathlib import Path
from datetime import timedelta

from prefect import flow, task, get_run_logger

from extract_deezer import main as extract_main
from load_deezer import main as load_main
from extract_musicbrainz import main as extract_mb_main
from load_musicbrainz import main as load_mb_main

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


@task(name="extract_musicbrainz")
def extract_musicbrainz():
    logger = get_run_logger()
    logger.info("Fetching MusicBrainz release dates for flagged tracks...")
    extract_mb_main()


@task(name="load_musicbrainz")
def load_musicbrainz():
    logger = get_run_logger()
    logger.info("Loading MusicBrainz releases into Snowflake...")
    load_mb_main()


@task(name="dbt_run")
def dbt_run():
    logger = get_run_logger()
    logger.info("Running dbt models...")
    result = subprocess.run(
        ["dbt", "run", "--profiles-dir", str(DBT_DIR)],
        cwd=DBT_DIR,
        capture_output=True,
        text=True,
    )
    logger.info(result.stdout)
    if result.returncode != 0:
        logger.error(result.stderr)
        raise RuntimeError(f"dbt run failed:\n{result.stderr}")


@flow(name="trackdown-pipeline")
def pipeline():
    extract()
    load()
    extract_musicbrainz()
    load_musicbrainz()
    dbt_run()


if __name__ == "__main__":
    import sys
    if "--serve" in sys.argv:
        pipeline.serve(name="trackdown-daily", interval=timedelta(days=1))
    else:
        pipeline()
