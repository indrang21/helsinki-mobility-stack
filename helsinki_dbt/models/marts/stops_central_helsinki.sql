{{ config(materialized='table') }}

with stops as (

    select * from {{ ref('stg_stops') }}

),

with_distance as (

    select
        gtfs_id,
        stop_name,
        vehicle_mode,
        latitude,
        longitude,
        round(
            sqrt(
                power((latitude - 60.1699) * 111, 2) + 
                power((longitude - 24.9384) * 55, 2)
            ) * 1000,
            0
        ) as distance_from_center_m
    from stops

),

central as (

    select *
    from with_distance
    where distance_from_center_m <= 2000

)

select * from central
order by distance_from_center_m