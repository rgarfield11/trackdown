# TrackDown

A music guessing game inspired by Heardle. Listen to a short clip and identify the song — each wrong guess or skip reveals a little more, along with clues to help you get there.

## How It Works

- You have **6 guesses** to identify the song from an audio clip
- The clip starts at **1 second** and grows by 1 second with each wrong guess or skip
- Search by song title or artist to make a guess
- Wrong guesses reveal clues: same artist, same genre, or release year within 5 years
- **Skip** to hear more without guessing — **Give Up** to reveal the answer

## Tech Stack

| Layer | Technology |
|---|---|
| Data extraction | Python, Deezer API |
| Data warehouse | Snowflake |
| Data transformation | dbt |
| Orchestration | Prefect |
| API | FastAPI |
| Frontend | Vue 3 |

## Project Structure

```
trackdown/
├── pipeline/
│   ├── extract.py      # Pulls tracks from Deezer decade playlists
│   ├── load.py         # Loads raw JSON into Snowflake
│   └── flow.py         # Prefect flow orchestrating the full pipeline
├── dbt/
│   └── models/
│       ├── staging/    # Flattens and types raw Deezer JSON
│       └── marts/      # Game-ready dim_tracks table
├── api/
│   └── main.py         # FastAPI — serves random tracks, search, and preview URLs
└── app/
    └── src/            # Vue 3 frontend
```

## Running Locally

### Prerequisites

- Python 3.12+
- Node.js 20+
- Snowflake account
- A `.env` file in the project root (see `.env.example`)

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the data pipeline

```bash
cd pipeline
python flow.py
```

### 3. Run dbt transformations

```bash
cd dbt
dbt run
```

### 4. Start the API

```bash
cd api
uvicorn main:app --reload
```

### 5. Start the frontend

```bash
cd app
npm install
npm run dev
```

Open `http://localhost:5173`.

## Data Pipeline

Tracks are sourced from Deezer's curated decade playlists (60s through 20s), enriched with album and genre metadata, and loaded into Snowflake as raw JSON. dbt transforms the raw layer into a clean `dim_tracks` mart table that powers the game.

Audio preview URLs are fetched fresh from Deezer at play time to avoid signed URL expiry.

## Contributing

Bug reports and pull requests are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR — the short version: branch off `main`, write tests alongside your changes, make sure CI is green.

## License

MIT
