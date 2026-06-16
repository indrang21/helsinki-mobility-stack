{{ config(materialized='table') }}

with stops as (

    select * from {{ ref('stg_stops') }}

),

aggregated as (

    select
        vehicle_mode,
        count(*) as total_stops,
        count(distinct stop_name) as unique_stop_names,
        round(avg(latitude), 4) as avg_latitude,
        round(avg(longitude), 4) as avg_longitude,
        min(latitude) as southernmost_lat,
        max(latitude) as northernmost_lat,
        current_timestamp as computed_at
    from stops
    group by vehicle_mode

)

select * from aggregated
order by total_stops desc