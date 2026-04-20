import json
import os
from dotenv import load_dotenv
import snowflake.connector

load_dotenv()

RAW_PATH = os.path.join(os.path.dirname(__file__), "data", "raw_musicbrainz.json")


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
        records = json.load(f)

    print(f"Loaded {len(records)} records from {RAW_PATH}")

    rows = [(json.dumps(record),) for record in records]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS TRACKDOWN.RAW.MUSICBRAINZ_RELEASES (
                    src VARIANT
                )
            """)
            cur.execute("CREATE TEMPORARY TABLE tmp_mb_releases (src VARIANT)")
            for row in rows:
                cur.execute(
                    "INSERT INTO tmp_mb_releases (src) SELECT PARSE_JSON(%s)",
                    row,
                )
            cur.execute("""
                MERGE INTO TRACKDOWN.RAW.MUSICBRAINZ_RELEASES t
                USING tmp_mb_releases s
                ON t.src:isrc::STRING = s.src:isrc::STRING
                WHEN MATCHED THEN UPDATE SET t.src = s.src
                WHEN NOT MATCHED THEN INSERT (src) VALUES (s.src)
            """)
            cur.execute("SELECT COUNT(*) FROM TRACKDOWN.RAW.MUSICBRAINZ_RELEASES")
            count = cur.fetchone()[0]

    print(f"Done! {count} rows in TRACKDOWN.RAW.MUSICBRAINZ_RELEASES")


if __name__ == "__main__":
    main()
