-- Release date accuracy analysis: Deezer vs MusicBrainz enrichment
-- Run with: dbt compile --select release_date_accuracy
-- Then execute the compiled SQL in Snowflake

with tracks as (
    select * from {{ ref('stg_tracks') }}
),

mb as (
    select * from {{ ref('stg_musicbrainz_releases') }}
),

joined as (
    select
        t.isrc,
        t.title,
        t.artist_name,
        t.album_title,
        t.release_date                          as deezer_date,
        t.release_year                          as deezer_year,
        try_to_date(mb.mb_release_date)         as mb_date,
        year(try_to_date(mb.mb_release_date))   as mb_year,

        mb.mb_release_date is not null
            and try_to_date(mb.mb_release_date) < t.release_date
            as mb_improved_date,

        case
            when mb.mb_release_date is not null
                and try_to_date(mb.mb_release_date) < t.release_date
            then t.release_year - year(try_to_date(mb.mb_release_date))
        end as years_corrected,

        (
            lower(t.title)       like '%remaster%' or lower(t.title)       like '%reissue%' or
            lower(t.album_title) like '%remaster%' or lower(t.album_title) like '%reissue%'
        ) as is_remaster_flagged

    from tracks t
    left join mb on t.isrc = mb.isrc
),

-- ── 1. Top-level summary ─────────────────────────────────────────────────────
summary as (
    select
        'SUMMARY'                                                        as section,
        count(*)                                                         as total_tracks,
        count(mb_date)                                                   as tracks_with_mb_data,
        round(count(mb_date) / count(*) * 100, 1)                       as mb_coverage_pct,
        sum(iff(mb_improved_date, 1, 0))                                 as tracks_date_corrected,
        round(
            sum(iff(mb_improved_date, 1, 0)) / nullif(count(mb_date), 0) * 100,
        1)                                                               as correction_rate_pct,
        round(avg(iff(mb_improved_date, years_corrected, null)), 1)      as avg_years_corrected,
        median(iff(mb_improved_date, years_corrected, null))             as median_years_corrected,
        max(iff(mb_improved_date, years_corrected, null))                as max_years_corrected,
        sum(iff(
            mb_improved_date
            and floor(deezer_year / 10) * 10 != floor(mb_year / 10) * 10,
        1, 0))                                                           as decade_shifts,
        sum(iff(is_remaster_flagged and mb_date is null, 1, 0))          as remaster_no_mb_match,
        sum(iff(is_remaster_flagged, 1, 0))                              as total_remaster_flagged
    from joined
),

-- ── 2. Biggest corrections ────────────────────────────────────────────────────
big_corrections as (
    select
        title,
        artist_name,
        album_title,
        deezer_year,
        mb_year,
        years_corrected
    from joined
    where mb_improved_date
    order by years_corrected desc
    limit 20
),

-- ── 3. Remaster-flagged tracks with no MB match (enrichment gaps) ─────────────
remaster_gaps as (
    select
        title,
        artist_name,
        album_title,
        deezer_year,
        isrc
    from joined
    where is_remaster_flagged
      and mb_date is null
    order by deezer_year desc
    limit 30
),

-- ── 4. Correction distribution by decade of corrected date ───────────────────
by_decade as (
    select
        floor(mb_year / 10) * 10   as original_decade,
        count(*)                    as tracks_corrected,
        round(avg(years_corrected), 1) as avg_years_corrected
    from joined
    where mb_improved_date
    group by 1
    order by 1
)

-- Change the final SELECT to whichever section you want to inspect:
--   summary / big_corrections / remaster_gaps / by_decade
select * from summary
