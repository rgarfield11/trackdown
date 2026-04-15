import json
import os
from dotenv import load_dotenv
import snowflake.connector

load_dotenv()

RAW_PATH = os.path.join(os.path.dirname(__file__), "data", "raw_tracks.json")


def get_connection():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
    )


def main():
    with open(RAW_PATH, encoding="utf-8") as f:
        tracks = json.load(f)

    print(f"Loaded {len(tracks)} tracks from {RAW_PATH}")

    rows = [(json.dumps(track),) for track in tracks]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE TRACKDOWN.RAW.TRACKS")
            for row in rows:
                cur.execute(
                    "INSERT INTO TRACKDOWN.RAW.TRACKS (src) SELECT PARSE_JSON(%s)",
                    row,
                )
            cur.execute("SELECT COUNT(*) FROM TRACKDOWN.RAW.TRACKS")
            count = cur.fetchone()[0]

    print(f"Done! {count} rows in TRACKDOWN.RAW.TRACKS")


if __name__ == "__main__":
    main()
