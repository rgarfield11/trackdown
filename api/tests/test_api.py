from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from main import app, strip_accents

# ---------------------------------------------------------------------------
# Sample data — mirrors the uppercase-keyed dicts Snowflake DictCursor returns
# ---------------------------------------------------------------------------

SAMPLE_TRACKS = [
    {
        "TRACK_ID": 1,
        "TITLE": "Bohemian Rhapsody",
        "ARTIST_NAME": "Queen",
        "ARTIST_ID": 412,
        "ALBUM_TITLE": "A Night at the Opera",
        "ALBUM_COVER_URL": "https://example.com/cover1.jpg",
        "PREVIEW_URL": "https://cdn.example.com/preview1.mp3",
        "RELEASE_YEAR": 1975,
        "DECADE": 1970,
        "GENRE_NAME": "Rock",
        "BPM": 72,
    },
    {
        "TRACK_ID": 2,
        "TITLE": "Smells Like Teen Spirit",
        "ARTIST_NAME": "Nirvana",
        "ARTIST_ID": 555,
        "ALBUM_TITLE": "Nevermind",
        "ALBUM_COVER_URL": "https://example.com/cover2.jpg",
        "PREVIEW_URL": "https://cdn.example.com/preview2.mp3",
        "RELEASE_YEAR": 1991,
        "DECADE": 1990,
        "GENRE_NAME": "Rock",
        "BPM": 116,
    },
    {
        "TRACK_ID": 3,
        "TITLE": "Café de Flore",
        "ARTIST_NAME": "Émile",
        "ARTIST_ID": 666,
        "ALBUM_TITLE": "Test Album",
        "ALBUM_COVER_URL": "https://example.com/cover3.jpg",
        "PREVIEW_URL": "https://cdn.example.com/preview3.mp3",
        "RELEASE_YEAR": 2000,
        "DECADE": 2000,
        "GENRE_NAME": "Pop",
        "BPM": 120,
    },
]

# 12 extra tracks used to verify the 10-result search cap
_EXTRA_TRACKS = [
    {
        "TRACK_ID": 100 + i,
        "TITLE": "Queen Song",
        "ARTIST_NAME": f"Artist {i}",
        "ARTIST_ID": 1000 + i,
        "ALBUM_TITLE": "Album",
        "ALBUM_COVER_URL": "",
        "PREVIEW_URL": "",
        "RELEASE_YEAR": 2000,
        "DECADE": 2000,
        "GENRE_NAME": "Pop",
        "BPM": 120,
    }
    for i in range(12)
]

ALL_TRACKS = SAMPLE_TRACKS + _EXTRA_TRACKS


def _make_mock_connection(tracks):
    """Build a mock Snowflake connection whose cursor returns *tracks*."""
    mock_cur = MagicMock()
    mock_cur.__enter__ = lambda s: mock_cur
    mock_cur.__exit__ = MagicMock(return_value=False)
    mock_cur.fetchall.return_value = tracks

    mock_conn = MagicMock()
    mock_conn.__enter__ = lambda s: mock_conn
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_conn.cursor.return_value = mock_cur
    return mock_conn


@pytest.fixture
def client():
    """TestClient with Snowflake mocked out; cache holds SAMPLE_TRACKS."""
    with patch("main.get_connection", return_value=_make_mock_connection(SAMPLE_TRACKS)):
        with TestClient(app) as c:
            yield c


@pytest.fixture
def client_large():
    """TestClient whose cache holds ALL_TRACKS (for limit-10 tests)."""
    with patch("main.get_connection", return_value=_make_mock_connection(ALL_TRACKS)):
        with TestClient(app) as c:
            yield c


# ---------------------------------------------------------------------------
# strip_accents — pure function, tested directly
# ---------------------------------------------------------------------------


def test_strip_accents_lowercases():
    assert strip_accents("Hello World") == "hello world"


def test_strip_accents_removes_acute():
    assert strip_accents("café") == "cafe"


def test_strip_accents_removes_various_diacritics():
    assert strip_accents("naïve") == "naive"
    assert strip_accents("Ñoño") == "nono"
    assert strip_accents("Émile") == "emile"


def test_strip_accents_empty_string():
    assert strip_accents("") == ""


def test_strip_accents_already_plain():
    assert strip_accents("queen") == "queen"


# ---------------------------------------------------------------------------
# GET /tracks/search
# ---------------------------------------------------------------------------


def test_search_empty_query_returns_empty(client):
    response = client.get("/tracks/search?q=")
    assert response.status_code == 200
    assert response.json() == []


def test_search_whitespace_query_returns_empty(client):
    response = client.get("/tracks/search?q=   ")
    assert response.status_code == 200
    assert response.json() == []


def test_search_matches_by_title(client):
    response = client.get("/tracks/search?q=Bohemian")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["TRACK_ID"] == 1


def test_search_matches_by_artist(client):
    response = client.get("/tracks/search?q=Nirvana")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["TRACK_ID"] == 2


def test_search_case_insensitive(client):
    response = client.get("/tracks/search?q=queen")
    assert response.status_code == 200
    results = response.json()
    assert any(r["TRACK_ID"] == 1 for r in results)


def test_search_accent_insensitive(client):
    # "cafe" should match "Café de Flore"
    response = client.get("/tracks/search?q=cafe")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["TRACK_ID"] == 3


def test_search_response_contains_only_allowed_fields(client):
    response = client.get("/tracks/search?q=Queen")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    allowed = {"TRACK_ID", "TITLE", "ARTIST_NAME", "ALBUM_COVER_URL", "RELEASE_YEAR"}
    for r in results:
        assert set(r.keys()) == allowed


def test_search_caps_at_ten_results(client_large):
    # There are 12+ tracks whose TITLE starts with "Queen Song"
    response = client_large.get("/tracks/search?q=Queen Song")
    assert response.status_code == 200
    assert len(response.json()) == 10


def test_search_no_match_returns_empty(client):
    response = client.get("/tracks/search?q=xyznonexistent")
    assert response.status_code == 200
    assert response.json() == []


# ---------------------------------------------------------------------------
# GET /tracks/random
# ---------------------------------------------------------------------------


def test_random_track_returns_cache_member(client):
    response = client.get("/tracks/random")
    assert response.status_code == 200
    data = response.json()
    sample_ids = {t["TRACK_ID"] for t in SAMPLE_TRACKS}
    assert data["TRACK_ID"] in sample_ids


# ---------------------------------------------------------------------------
# GET /tracks/{track_id}/preview
# ---------------------------------------------------------------------------


def test_preview_redirects_to_deezer_url(client):
    mock_response = MagicMock()
    mock_response.json.return_value = {"preview": "https://cdn.deezer.com/preview/abc.mp3"}
    with patch("main.http_requests.get", return_value=mock_response):
        response = client.get("/tracks/123/preview", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://cdn.deezer.com/preview/abc.mp3"


def test_preview_returns_404_when_no_preview(client):
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 123}  # no "preview" key
    with patch("main.http_requests.get", return_value=mock_response):
        response = client.get("/tracks/123/preview")
    assert response.status_code == 404
