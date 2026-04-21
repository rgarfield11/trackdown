import requests
import json
import time
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "https://api.deezer.com"

PLAYLISTS = {
    "hits_60s": 620264073,
    "hits_70s": 1470022445,
    "hits_80s": 867825522,
    "hits_90s": 1026896351,
    "hits_00s": 248297032,
    "hits_10s": 907257825,
    "hits_20s": 13650084141,
}

GENRE_CHARTS = {
    "pop": 132,
    "rock": 152,
    "rap_hip_hop": 116,
    "r_and_b": 165,
    "soul_and_funk": 169,
}

def get_playlist_tracks(playlist_id):
    """Pull tracks from a specific playlist."""
    url = f"{BASE_URL}/playlist/{playlist_id}/tracks"
    response = requests.get(url)
    response.raise_for_status()
    return response.json().get("data", [])

def get_genre_chart_tracks(genre_id, limit=100):
    """Pull top tracks from a genre chart, paginating up to limit."""
    tracks = []
    index = 0
    page_size = 50
    while len(tracks) < limit:
        url = f"{BASE_URL}/chart/{genre_id}/tracks?limit={page_size}&index={index}"
        response = requests.get(url)
        response.raise_for_status()
        page = response.json().get("data", [])
        if not page:
            break
        tracks.extend(page)
        if len(page) < page_size:
            break
        index += page_size
        time.sleep(0.3)
    return tracks[:limit]

def enrich_track(track_id):
    """Get full track details including BPM and release info."""
    url = f"{BASE_URL}/track/{track_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def enrich_album(album_id):
    """Get album details including release date and genre label."""
    url = f"{BASE_URL}/album/{album_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def build_track_record(track, track_detail, album_detail):
    """Merge chart, track, and album data into one flat record."""
    return {
        # Core identifiers
        "track_id": track["id"],
        "title": track["title"],
        "duration_seconds": track["duration"],
        "preview_url": track.get("preview"),
        "explicit": track.get("explicit_lyrics", False),

        # Chart metadata
        "chart_position": track.get("position"),
        "rank": track.get("rank"),

        # Artist
        "artist_id": track["artist"]["id"],
        "artist_name": track["artist"]["name"],

        # Album
        "album_id": track["album"]["id"],
        "album_title": track["album"]["title"],
        "album_cover_medium": track["album"].get("cover_medium"),

        # Enriched track fields
        "bpm": track_detail.get("bpm"),
        "gain": track_detail.get("gain"),
        "isrc": track_detail.get("isrc"),

        # Enriched album fields
        "release_date": album_detail.get("release_date"),
        "release_year": int(album_detail["release_date"][:4]) if album_detail.get("release_date") else None,
        "genre_id": album_detail.get("genre_id"),
        "genre_name": next(iter(album_detail.get("genres", {}).get("data", [])), {}).get("name"),
        "record_type": album_detail.get("record_type"),
        "label": album_detail.get("label"),
    }

def load_existing_tracks(output_path):
    """Return a dict of already-enriched tracks keyed by track_id."""
    if not os.path.exists(output_path):
        return {}
    with open(output_path, encoding="utf-8") as f:
        tracks = json.load(f)
    return {t["track_id"]: t for t in tracks if t.get("track_id")}


def main():
    print("Fetching tracks from Deezer playlists...")

    output_path = os.path.join(os.path.dirname(__file__), "data", "raw_tracks.json")
    existing_tracks = load_existing_tracks(output_path)
    print(f"Found {len(existing_tracks)} already-enriched tracks in cache.")

    # Step 1: Collect unique track stubs from all playlists
    all_track_stubs = {}

    for playlist_name, playlist_id in PLAYLISTS.items():
        print(f"  -> {playlist_name} playlist")
        for track in get_playlist_tracks(playlist_id):
            if track.get("id"):
                all_track_stubs[track["id"]] = track
        time.sleep(0.5)

    for genre_name, genre_id in GENRE_CHARTS.items():
        print(f"  -> {genre_name} genre chart")
        for track in get_genre_chart_tracks(genre_id, limit=10):
            if track.get("id"):
                all_track_stubs[track["id"]] = track
        time.sleep(0.5)

    new_stubs = {tid: stub for tid, stub in all_track_stubs.items() if tid not in existing_tracks}
    print(f"\nCollected {len(all_track_stubs)} unique tracks ({len(new_stubs)} new). Enriching new tracks...")

    # Step 2: Enrich each new track with full details
    newly_enriched = []
    for i, (track_id, track_stub) in enumerate(new_stubs.items(), 1):

        if not track_stub.get("preview"):
            print(f"  [{i}/{len(new_stubs)}] Skipping (no preview): {track_stub['title']}")
            continue

        print(f"  [{i}/{len(new_stubs)}] Enriching: {track_stub['title']} - {track_stub['artist']['name']}")

        try:
            track_detail = enrich_track(track_id)
            time.sleep(0.3)

            album_id = track_stub["album"]["id"]
            album_detail = enrich_album(album_id)
            time.sleep(0.3)

            record = build_track_record(track_stub, track_detail, album_detail)
            newly_enriched.append(record)

        except Exception as e:
            print(f"    ! Error enriching track {track_id}: {e}")
            continue

    enriched_tracks = list(existing_tracks.values()) + newly_enriched
    print(f"\n{len(newly_enriched)} new tracks enriched. {len(enriched_tracks)} total.")

    # Step 3: Save to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched_tracks, f, indent=2)

    print(f"\nDone! {len(enriched_tracks)} tracks saved to {output_path}")

    # Quick summary
    with_preview = sum(1 for t in enriched_tracks if t.get("preview_url"))
    with_release = sum(1 for t in enriched_tracks if t.get("release_year"))
    with_genre   = sum(1 for t in enriched_tracks if t.get("genre_name"))
    with_bpm     = sum(1 for t in enriched_tracks if t.get("bpm"))

    print(f"\nData quality summary:")
    print(f"  Preview URL : {with_preview}/{len(enriched_tracks)}")
    print(f"  Release year: {with_release}/{len(enriched_tracks)}")
    print(f"  Genre name  : {with_genre}/{len(enriched_tracks)}")
    print(f"  BPM         : {with_bpm}/{len(enriched_tracks)}")

if __name__ == "__main__":
    main()
