import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from extract_musicbrainz import clean_title, get_earliest_release_date, load_existing_releases


# ---------------------------------------------------------------------------
# clean_title
# ---------------------------------------------------------------------------

def test_clean_title_strips_remaster_parentheses():
    assert clean_title("Come Together (Remastered 2009)") == "Come Together"

def test_clean_title_strips_remaster_brackets():
    assert clean_title("Come Together [Remastered 2009]") == "Come Together"

def test_clean_title_strips_year_only_parentheses():
    assert clean_title("Bad Moon Rising (Remastered 1985)") == "Bad Moon Rising"

def test_clean_title_no_suffix_unchanged():
    assert clean_title("Smells Like Teen Spirit") == "Smells Like Teen Spirit"

def test_clean_title_multiple_parentheses():
    assert clean_title("Song (Live) (Remastered 2009)") == "Song"

def test_clean_title_strips_whitespace():
    assert clean_title("Yesterday  (Remastered 2009)") == "Yesterday"


# ---------------------------------------------------------------------------
# get_earliest_release_date
# ---------------------------------------------------------------------------

def _mock_response(recordings):
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {"recordings": recordings}
    return mock


def test_get_earliest_release_date_returns_earliest():
    recordings = [
        {"score": 100, "first-release-date": "1969-09-26", "artist-credit": [{"artist": {"name": "The Beatles"}}]},
        {"score": 95, "first-release-date": "2009-09-09", "artist-credit": [{"artist": {"name": "The Beatles"}}]},
    ]
    with patch("extract_musicbrainz.requests.get", return_value=_mock_response(recordings)):
        result = get_earliest_release_date("Come Together (Remastered 2009)", "The Beatles")
    assert result == "1969-09-26"


def test_get_earliest_release_date_filters_wrong_artist():
    recordings = [
        {"score": 92, "first-release-date": "1965-01-01", "artist-credit": [{"artist": {"name": "Some Cover Artist"}}]},
        {"score": 98, "first-release-date": "1969-09-26", "artist-credit": [{"artist": {"name": "The Beatles"}}]},
    ]
    with patch("extract_musicbrainz.requests.get", return_value=_mock_response(recordings)):
        result = get_earliest_release_date("Yesterday (Remastered 2009)", "The Beatles")
    assert result == "1969-09-26"


def test_get_earliest_release_date_the_prefix_insensitive():
    recordings = [
        {"score": 91, "first-release-date": "2009-06-15", "artist-credit": [{"artist": {"name": "Black Eyed Peas"}}]},
    ]
    with patch("extract_musicbrainz.requests.get", return_value=_mock_response(recordings)):
        result = get_earliest_release_date("I Gotta Feeling", "The Black Eyed Peas")
    assert result == "2009-06-15"


def test_get_earliest_release_date_no_matches_returns_none():
    recordings = [
        {"score": 95, "first-release-date": "1969-09-26", "artist-credit": [{"artist": {"name": "Someone Else"}}]},
    ]
    with patch("extract_musicbrainz.requests.get", return_value=_mock_response(recordings)):
        result = get_earliest_release_date("Come Together (Remastered 2009)", "The Beatles")
    assert result is None


def test_get_earliest_release_date_404_returns_none():
    mock = MagicMock()
    mock.status_code = 404
    with patch("extract_musicbrainz.requests.get", return_value=mock):
        result = get_earliest_release_date("Come Together (Remastered 2009)", "The Beatles")
    assert result is None


def test_get_earliest_release_date_filters_low_score():
    recordings = [
        {"score": 45, "first-release-date": "1955-01-01", "artist-credit": [{"artist": {"name": "The Beatles"}}]},
        {"score": 95, "first-release-date": "1969-09-26", "artist-credit": [{"artist": {"name": "The Beatles"}}]},
    ]
    with patch("extract_musicbrainz.requests.get", return_value=_mock_response(recordings)):
        result = get_earliest_release_date("Come Together (Remastered 2009)", "The Beatles")
    assert result == "1969-09-26"


def test_get_earliest_release_date_skips_recordings_without_date():
    recordings = [
        {"score": 100, "artist-credit": [{"artist": {"name": "The Beatles"}}]},
        {"score": 100, "first-release-date": "1969-09-26", "artist-credit": [{"artist": {"name": "The Beatles"}}]},
    ]
    with patch("extract_musicbrainz.requests.get", return_value=_mock_response(recordings)):
        result = get_earliest_release_date("Come Together (Remastered 2009)", "The Beatles")
    assert result == "1969-09-26"


# ---------------------------------------------------------------------------
# load_existing_releases
# ---------------------------------------------------------------------------

def test_load_existing_releases_returns_empty_when_no_file():
    result = load_existing_releases("/nonexistent/path/raw_musicbrainz.json")
    assert result == {}


def test_load_existing_releases_keys_by_isrc(tmp_path):
    data = [
        {"isrc": "USUM71703861", "mb_release_date": "1969-09-26"},
        {"isrc": "GBAYE6800011", "mb_release_date": "1965-03-22"},
    ]
    f = tmp_path / "raw_musicbrainz.json"
    f.write_text(__import__("json").dumps(data), encoding="utf-8")
    result = load_existing_releases(str(f))
    assert set(result.keys()) == {"USUM71703861", "GBAYE6800011"}


def test_load_existing_releases_skips_entries_without_isrc(tmp_path):
    data = [{"isrc": "USUM71703861", "mb_release_date": "1969-09-26"}, {"mb_release_date": "2000-01-01"}]
    f = tmp_path / "raw_musicbrainz.json"
    f.write_text(__import__("json").dumps(data), encoding="utf-8")
    result = load_existing_releases(str(f))
    assert list(result.keys()) == ["USUM71703861"]
