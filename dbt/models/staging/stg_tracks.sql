with source as (
    select src from {{ source('raw', 'tracks') }}
),

flattened as (
    select
        src:track_id::integer       as track_id,
        src:title::varchar          as title,
        src:preview_url::varchar    as preview_url,
        src:explicit::boolean       as explicit,

        src:artist_id::integer      as artist_id,
        src:artist_name::varchar    as artist_name,

        src:album_id::integer       as album_id,
        src:album_title::varchar    as album_title,
        src:album_cover_medium::varchar as album_cover_url,

        src:release_date::date      as release_date,
        src:release_year::integer   as release_year,
        floor(src:release_year::integer / 10) * 10 as decade,

        src:genre_id::integer       as genre_id,
        src:genre_name::varchar     as genre_name,

        src:bpm::float              as bpm,
        src:duration_seconds::integer as duration_seconds,
        src:label::varchar          as label,
        src:record_type::varchar    as record_type,
        src:isrc::varchar           as isrc

    from source
)

select * from flattened
where preview_url is not null
