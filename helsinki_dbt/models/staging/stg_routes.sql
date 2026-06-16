{{ config(materialized='view') }}

with source as (

    select * from {{ source('raw', 'routes') }}

),

cleaned as (

    select
        gtfs_id,
        trim(short_name) as short_name,
        trim(long_name) as long_name,
        upper(coalesce(mode, 'UNKNOWN')) as mode,
        type as route_type_code,
        case 
            when type = 0 then 'Tram'
            when type = 1 then 'Subway'
            when type = 2 then 'Rail'
            when type = 3 then 'Bus'
            when type = 4 then 'Ferry'
            when type = 109 then 'Suburban Rail'
            when type = 700 then 'Bus Service'
            when type = 701 then 'Regional Bus'
            when type = 702 then 'Express Bus'
            when type = 704 then 'Local Bus'
            when type = 900 then 'Tram Service'
            when type = 1000 then 'Water Transport'
            else 'Other'
        end as route_type_name,
        description,
        loaded_at
    from source
    where short_name is not null

)

select * from cleaned