with source as (
    select src from {{ source('raw', 'musicbrainz_releases') }}
),

flattened as (
    select
        src:isrc::varchar           as isrc,
        src:mb_release_date::varchar as mb_release_date
    from source
    where src:mb_release_date is not null
)

select * from flattened
