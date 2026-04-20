import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from extract_deezer import build_track_record

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

TRACK_STUB = {
    "id": 123,
    "title": "Bohemian Rhapsody",
    "duration": 355,
    "preview": "https://cdns-preview.deezer.com/stream/abc.mp3",
    "explicit_lyrics": True,
    "position": 1,
    "rank": 950000,
    "artist": {"id": 412, "name": "Queen"},
    "album": {
        "id": 789,
        "title": "A Night at the Opera",
        "cover_medium": "https://e-cdns.dzimg.com/abc",
    },
}

TRACK_DETAIL = {
    "bpm": 72.0,
    "gain": -12.3,
    "isrc": "GBBBN7500066",
}

ALBUM_DETAIL = {
    "release_date": "1975-11-21",
    "genre_id": 152,
    "genres": {"data": [{"id": 152, "name": "Rock"}]},
    "record_type": "album",
    "label": "EMI",
}


# ---------------------------------------------------------------------------
# Happy-path: all fields present
# ---------------------------------------------------------------------------


def test_build_track_record_core_identifiers():
    record = build_track_record(TRACK_STUB, TRACK_DETAIL, ALBUM_DETAIL)
    assert record["track_id"] == 123
    assert record["title"] == "Bohemian Rhapsody"
    assert record["duration_seconds"] == 355
    assert record["preview_url"] == "https://cdns-preview.deezer.com/stream/abc.mp3"
    assert record["explicit"] is True


def test_build_track_record_artist_fields():
    record = build_track_record(TRACK_STUB, TRACK_DETAIL, ALBUM_DETAIL)
    assert record["artist_id"] == 412
    assert record["artist_name"] == "Queen"


def test_build_track_record_album_fields():
    record = build_track_record(TRACK_STUB, TRACK_DETAIL, ALBUM_DETAIL)
    assert record["album_id"] == 789
    assert record["album_title"] == "A Night at the Opera"
    assert record["album_cover_medium"] == "https://e-cdns.dzimg.com/abc"


def test_build_track_record_enriched_track_fields():
    record = build_track_record(TRACK_STUB, TRACK_DETAIL, ALBUM_DETAIL)
    assert record["bpm"] == 72.0
    assert record["gain"] == -12.3
    assert record["isrc"] == "GBBBN7500066"


def test_build_track_record_enriched_album_fields():
    record = build_track_record(TRACK_STUB, TRACK_DETAIL, ALBUM_DETAIL)
    assert record["release_date"] == "1975-11-21"
    assert record["release_year"] == 1975
    assert record["genre_id"] == 152
    assert record["genre_name"] == "Rock"
    assert record["record_type"] == "album"
    assert record["label"] == "EMI"


# ---------------------------------------------------------------------------
# Optional / edge cases
# ---------------------------------------------------------------------------


def test_build_track_record_no_preview_url():
    track = {k: v for k, v in TRACK_STUB.items() if k != "preview"}
    record = build_track_record(track, TRACK_DETAIL, ALBUM_DETAIL)
    assert record["preview_url"] is None


def test_build_track_record_explicit_defaults_to_false():
    track = {k: v for k, v in TRACK_STUB.items() if k != "explicit_lyrics"}
    record = build_track_record(track, TRACK_DETAIL, ALBUM_DETAIL)
    assert record["explicit"] is False


def test_build_track_record_no_release_date():
    album = {**ALBUM_DETAIL, "release_date": None}
    record = build_track_record(TRACK_STUB, TRACK_DETAIL, album)
    assert record["release_date"] is None
    assert record["release_year"] is None


def test_build_track_record_release_year_extracted_from_date():
    album = {**ALBUM_DETAIL, "release_date": "2001-03-15"}
    record = build_track_record(TRACK_STUB, TRACK_DETAIL, album)
    assert record["release_year"] == 2001


def test_build_track_record_no_genres_key():
    album = {k: v for k, v in ALBUM_DETAIL.items() if k != "genres"}
    record = build_track_record(TRACK_STUB, TRACK_DETAIL, album)
    assert record["genre_name"] is None


def test_build_track_record_empty_genres_data():
    """genres.data exists but is an empty list — should return None, not raise."""
    album = {**ALBUM_DETAIL, "genres": {"data": []}}
    record = build_track_record(TRACK_STUB, TRACK_DETAIL, album)
    assert record["genre_name"] is None


def test_build_track_record_chart_metadata():
    record = build_track_record(TRACK_STUB, TRACK_DETAIL, ALBUM_DETAIL)
    assert record["chart_position"] == 1
    assert record["rank"] == 950000
