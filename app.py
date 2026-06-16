import streamlit as st
import duckdb
import plotly.express as px

st.title("Helsinki Mobility Dashboard")

con = duckdb.connect("helsinki.db", read_only=True)

# KPI metrics row
total_stops_count = con.execute("SELECT SUM(total_stops) FROM main_marts.stops_by_mode").fetchone()[0]
total_modes = con.execute("SELECT COUNT(DISTINCT vehicle_mode) FROM main_marts.stops_by_mode").fetchone()[0]
total_routes = con.execute("SELECT COUNT(*) FROM main_staging.stg_routes").fetchone()[0]
central_stops = con.execute("SELECT COUNT(*) FROM main_marts.stops_central_helsinki").fetchone()[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Stops", f"{total_stops_count:,}")
col2.metric("Vehicle Modes", total_modes)
col3.metric("Active Routes", total_routes)
col4.metric("Central Stops (2km)", central_stops)

st.divider()

df = con.execute("SELECT * FROM main_marts.stops_by_mode").df()
st.dataframe(df)

st.header("Stops per vehicle mode")

fig = px.bar(
    df,
    x="vehicle_mode",
    y="total_stops",
    color="vehicle_mode",
    text="total_stops"
)

st.plotly_chart(fig, use_container_width=True)

st.header("Stops Map — Central Helsinki")

map_df = con.execute("""
    SELECT 
        stop_name,
        vehicle_mode,
        latitude,
        longitude,
        distance_from_center_m,
        CASE vehicle_mode
            WHEN 'BUS' THEN '#FF5733'
            WHEN 'TRAM' THEN '#33A1FF'
            WHEN 'RAIL' THEN '#33FF57'
            WHEN 'SUBWAY' THEN '#FF33A1'
            WHEN 'FERRY' THEN '#A133FF'
            ELSE '#808080'
        END AS color
    FROM main_marts.stops_central_helsinki
""").df()

st.map(
    map_df,
    latitude="latitude",
    longitude="longitude",
    color="color",
    size=20
)