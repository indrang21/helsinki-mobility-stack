{{ config(materialized='table') }}

with routes as (

    select * from {{ ref('stg_routes') }}

),

aggregated as (

    select
        mode,
        route_type_name,
        count(*) as total_routes,
        count(distinct short_name) as unique_route_names,
        count(case when long_name is not null and long_name != '' then 1 end) as routes_with_description,
        current_timestamp as computed_at
    from routes
    group by mode, route_type_name

)

select * from aggregated
order by total_routes desc