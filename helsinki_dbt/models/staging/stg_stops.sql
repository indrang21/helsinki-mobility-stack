{{ config(materialized='view') }}

with source as (

    select * from {{ source('raw', 'stops') }}

),

cleaned as (

    select
        gtfs_id,
        trim(name) as stop_name,
        lat as latitude,
        lon as longitude,
        upper(coalesce(vehicle_mode, 'UNKNOWN')) as vehicle_mode,
        loaded_at
    from source
    where lat is not null
      and lon is not null
      and lat between -90 and 90
      and lon between -180 and 180

)

select * from cleaned