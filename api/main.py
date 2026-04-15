import os
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import snowflake.connector
import requests as http_requests

load_dotenv()

app = FastAPI(title="TrackDown API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def get_connection():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        schema="MARTS",
    )


@app.get("/tracks/random")
def random_track():
    """Return a single random playable track."""
    with get_connection() as conn:
        with conn.cursor(snowflake.connector.DictCursor) as cur:
            cur.execute("""
                SELECT
                    track_id, title, artist_name, album_title,
                    album_cover_url, preview_url, release_year,
                    decade, genre_name, artist_id, bpm
                FROM dim_tracks
                ORDER BY RANDOM()
                LIMIT 1
            """)
            return cur.fetchone()


@app.get("/tracks/{track_id}/preview")
def track_preview(track_id: int):
    """Fetch a fresh preview URL from Deezer and redirect to it."""
    res = http_requests.get(f"https://api.deezer.com/track/{track_id}", timeout=5)
    res.raise_for_status()
    data = res.json()
    preview_url = data.get("preview")
    if not preview_url:
        raise HTTPException(status_code=404, detail="No preview available for this track")
    return RedirectResponse(url=preview_url)


@app.get("/tracks/search")
def search_tracks(q: str = Query(min_length=1)):
    """Search tracks by title or artist for the guess dropdown."""
    with get_connection() as conn:
        with conn.cursor(snowflake.connector.DictCursor) as cur:
            cur.execute("""
                SELECT
                    track_id, title, artist_name,
                    album_cover_url, release_year
                FROM dim_tracks
                WHERE LOWER(title) LIKE LOWER(%s)
                   OR LOWER(artist_name) LIKE LOWER(%s)
                ORDER BY title
                LIMIT 10
            """, (f"%{q}%", f"%{q}%"))
            return cur.fetchall()
