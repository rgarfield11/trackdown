import re
import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://musicbrainz.org/ws/2"
HEADERS = {"User-Agent": "TrackDown/1.0 (rossgarfield@gmail.com)"}

REMASTER_KEYWORDS = ["remaster", "reissue"]

def get_connection():
    import snowflake.connector
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
    )


def get_flagged_tracks():
    keyword_conditions = " OR ".join(
        f"LOWER(TITLE) LIKE '%{kw}%' OR LOWER(ALBUM_TITLE) LIKE '%{kw}%'"
        for kw in REMASTER_KEYWORDS
    )
    query = f"""
        SELECT ISRC, TITLE, ARTIST_NAME
        FROM TRACKDOWN.STAGING.STG_TRACKS
        WHERE {keyword_conditions}
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return [
                {"isrc": row[0], "title": row[1], "artist_name": row[2]}
                for row in cur.fetchall()
            ]


def clean_title(title):
    return re.sub(r"\s*[\(\[].*?[\)\]]", "", title).strip()


def get_earliest_release_date(title, artist_name):
    clean = clean_title(title)
    url = f"{BASE_URL}/recording"
    params = {
        "query": f'recording:"{clean}" AND artist:"{artist_name}"',
        "fmt": "json",
        "limit": 100,
    }
    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code == 404:
        return None
    response.raise_for_status()

    dates = [
        r["first-release-date"]
        for r in response.json().get("recordings", [])
        if r.get("first-release-date")
        and any(
            credit["artist"]["name"].lower().removeprefix("the ") == artist_name.lower().removeprefix("the ")
            for credit in r.get("artist-credit", [])
            if "artist" in credit
        )
    ]

    return min(dates) if dates else None


def main():
    print("Fetching flagged tracks from Snowflake...")
    flagged = get_flagged_tracks()
    print(f"Found {len(flagged)} flagged tracks to enrich")

    results = []
    for i, track in enumerate(flagged, 1):
        print(f"  [{i}/{len(flagged)}] {track['title']} - {track['artist_name']}")

        try:
            earliest_date = get_earliest_release_date(track["title"], track["artist_name"])
            results.append({
                "isrc": track["isrc"],
                "title": track["title"],
                "artist_name": track["artist_name"],
                "mb_release_date": earliest_date,
            })
            print(f"    -> {earliest_date or 'not found'}")
        except Exception as e:
            print(f"    ! Error: {e}")

        time.sleep(1.1)

    output_path = os.path.join(os.path.dirname(__file__), "data", "raw_musicbrainz.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    found = sum(1 for r in results if r["mb_release_date"])
    print(f"\nDone! {found}/{len(results)} tracks enriched, saved to {output_path}")


if __name__ == "__main__":
    main()
