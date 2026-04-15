with tracks as (
    select * from {{ ref('stg_tracks') }}
)

select
    track_id,
    title,
    preview_url,
    explicit,

    artist_id,
    artist_name,

    album_id,
    album_title,
    album_cover_url,

    release_date,
    release_year,
    decade,

    genre_id,
    genre_name,

    duration_seconds,
    bpm,
    label,
    record_type,
    isrc

from tracks
