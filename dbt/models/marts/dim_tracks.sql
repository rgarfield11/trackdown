with tracks as (
    select * from {{ ref('stg_tracks') }}
),

mb as (
    select * from {{ ref('stg_musicbrainz_releases') }}
),

enriched as (
    select
        t.track_id,
        t.title,
        t.preview_url,
        t.explicit,

        t.artist_id,
        t.artist_name,

        t.album_id,
        t.album_title,
        t.album_cover_url,

        case
            when mb.mb_release_date is not null
                and try_to_date(mb.mb_release_date) < t.release_date
            then try_to_date(mb.mb_release_date)
            else t.release_date
        end as release_date,

        case
            when mb.mb_release_date is not null
                and try_to_date(mb.mb_release_date) < t.release_date
            then year(try_to_date(mb.mb_release_date))
            else t.release_year
        end as release_year,

        case
            when mb.mb_release_date is not null
                and try_to_date(mb.mb_release_date) < t.release_date
            then floor(year(try_to_date(mb.mb_release_date)) / 10) * 10
            else t.decade
        end as decade,

        t.genre_id,
        t.genre_name,

        t.duration_seconds,
        t.bpm,
        t.label,
        t.record_type,
        t.isrc

    from tracks t
    left join mb on t.isrc = mb.isrc
)

select * from enriched
qualify row_number() over (
    partition by coalesce(isrc, track_id::varchar)
    order by release_date asc nulls last
) = 1
