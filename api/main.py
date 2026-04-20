import os
import unicodedata
import random
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import snowflake.connector
import requests as http_requests

load_dotenv()

track_cache: list[dict] = []


def get_connection():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        schema="MARTS",
    )


def normalize_text(s: str) -> str:
    # Strip accents, then remove apostrophes/punctuation so "wasnt" matches "wasn't"
    without_accents = ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )
    return ''.join(c for c in without_accents if c.isalnum() or c.isspace()).lower()


@asynccontextmanager
async def lifespan(app: FastAPI):
    with get_connection() as conn:
        with conn.cursor(snowflake.connector.DictCursor) as cur:
            cur.execute("""
                SELECT
                    track_id, title, artist_name, album_title,
                    album_cover_url, preview_url, release_year,
                    decade, genre_name, artist_id, bpm
                FROM dim_tracks
            """)
            track_cache.extend(cur.fetchall())
    print(f"Loaded {len(track_cache)} tracks into cache")
    yield
    track_cache.clear()


app = FastAPI(title="TrackDown API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://192.168.0.89:5173",
        "https://trackdown-production-52f0.up.railway.app",
    ],
    # Matches production alias and all Vercel preview deployments, e.g.
    # trackdown-amber.vercel.app, trackdown-feat-xyz-rgarfield11s-projects.vercel.app
    allow_origin_regex=r"https://trackdown[a-zA-Z0-9-]*\.vercel\.app",
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/tracks/random")
def random_track():
    """Return a single random playable track."""
    return random.choice(track_cache)


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
def search_tracks(q: str):
    """Search tracks by title or artist for the guess dropdown."""
    if not q.strip():
        return []
    normalized_q = normalize_text(q.strip())
    results = [
        t for t in track_cache
        if normalized_q in normalize_text(t["TITLE"])
        or normalized_q in normalize_text(t["ARTIST_NAME"])
    ]
    return [
        {
            "TRACK_ID": t["TRACK_ID"],
            "TITLE": t["TITLE"],
            "ARTIST_NAME": t["ARTIST_NAME"],
            "ALBUM_COVER_URL": t["ALBUM_COVER_URL"],
            "RELEASE_YEAR": t["RELEASE_YEAR"],
        }
        for t in results[:10]
    ]
