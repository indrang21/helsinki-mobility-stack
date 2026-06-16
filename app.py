import streamlit as st
import duckdb
import plotly.express as px
import requests
import json
import os

st.set_page_config(page_title="Helsinki Mobility Dashboard", layout="wide")

# ============================================================
# CONFIG
# ============================================================
HSL_API_URL = "https://api.digitransit.fi/routing/v2/hsl/gtfs/v1"

def get_api_key():
    """Get key from Streamlit Cloud secrets OR local .env file"""
    try:
        return st.secrets["HSL_API_KEY"]
    except Exception:
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv("HSL_API_KEY")

API_KEY = get_api_key()

# ============================================================
# DATA FETCH (cached 1 hour)
# ============================================================
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_hsl_data():
    headers = {
        "Content-Type": "application/json",
        "digitransit-subscription-key": API_KEY
    }
    
    stops_query = "{ stops { gtfsId name lat lon vehicleMode } }"
    routes_query = "{ routes { gtfsId shortName longName mode type } }"
    
    stops_res = requests.post(HSL_API_URL, json={"query": stops_query}, headers=headers)
    stops_res.raise_for_status()
    
    routes_res = requests.post(HSL_API_URL, json={"query": routes_query}, headers=headers)
    routes_res.raise_for_status()
    
    return stops_res.json()["data"]["stops"], routes_res.json()["data"]["routes"]

# ============================================================
# IN-MEMORY DUCKDB WITH MEDALLION ARCHITECTURE
# ============================================================
@st.cache_resource(show_spinner=False)
def build_database(_stops, _routes):
    import pandas as pd
    
    con = duckdb.connect(":memory:")
    
    # Convert API data to DataFrames
    stops_df = pd.DataFrame(_stops)
    routes_df = pd.DataFrame(_routes)
    
    # Register as DuckDB tables
    con.register("stops_raw", stops_df)
    con.register("routes_raw", routes_df)
    
    # Bronze layer
    con.execute("CREATE SCHEMA raw")
    con.execute("""
        CREATE TABLE raw.stops AS
        SELECT 
            gtfsId AS gtfs_id,
            name,
            CAST(lat AS DOUBLE) AS lat,
            CAST(lon AS DOUBLE) AS lon,
            vehicleMode AS vehicle_mode
        FROM stops_raw
    """)
    
    con.execute("""
        CREATE TABLE raw.routes AS
        SELECT 
            gtfsId AS gtfs_id,
            shortName AS short_name,
            longName AS long_name,
            mode
        FROM routes_raw
    """)
    
    # Silver layer
    con.execute("CREATE SCHEMA staging")
    con.execute("""
        CREATE VIEW staging.stg_stops AS
        SELECT
            gtfs_id,
            TRIM(name) AS stop_name,
            lat AS latitude,
            lon AS longitude,
            UPPER(COALESCE(vehicle_mode, 'UNKNOWN')) AS vehicle_mode
        FROM raw.stops
        WHERE lat BETWEEN -90 AND 90 AND lon BETWEEN -180 AND 180
    """)
    
    con.execute("""
        CREATE VIEW staging.stg_routes AS
        SELECT
            gtfs_id,
            TRIM(short_name) AS short_name,
            TRIM(long_name) AS long_name,
            UPPER(COALESCE(mode, 'UNKNOWN')) AS mode
        FROM raw.routes
        WHERE short_name IS NOT NULL
    """)
    
    # Gold layer
    con.execute("CREATE SCHEMA marts")
    con.execute("""
        CREATE TABLE marts.stops_by_mode AS
        SELECT
            vehicle_mode,
            COUNT(*) AS total_stops,
            COUNT(DISTINCT stop_name) AS unique_stop_names
        FROM staging.stg_stops
        GROUP BY vehicle_mode
        ORDER BY total_stops DESC
    """)
    
    con.execute("""
        CREATE TABLE marts.stops_central_helsinki AS
        SELECT
            gtfs_id, stop_name, vehicle_mode, latitude, longitude,
            ROUND(SQRT(POWER((latitude - 60.1699) * 111, 2) + 
                       POWER((longitude - 24.9384) * 55, 2)) * 1000, 0) AS distance_from_center_m,
            CASE vehicle_mode
                WHEN 'BUS' THEN '#FF5733'
                WHEN 'TRAM' THEN '#33A1FF'
                WHEN 'RAIL' THEN '#33FF57'
                WHEN 'SUBWAY' THEN '#FF33A1'
                WHEN 'FERRY' THEN '#A133FF'
                ELSE '#808080'
            END AS color
        FROM staging.stg_stops
        WHERE SQRT(POWER((latitude - 60.1699) * 111, 2) + 
                   POWER((longitude - 24.9384) * 55, 2)) * 1000 <= 2000
        ORDER BY distance_from_center_m
    """)
    
    return con

# ============================================================
# UI
# ============================================================
st.title("🚌 Helsinki Mobility Dashboard")
st.caption("Live data from HSL Digitransit API • Auto-refresh every hour")

if not API_KEY:
    st.error("HSL_API_KEY not configured. Add it to Streamlit secrets or .env file.")
    st.stop()

with st.spinner("Fetching live Helsinki transit data..."):
    stops, routes = fetch_hsl_data()
    con = build_database(stops, routes)

# KPI row
total_stops = con.execute("SELECT SUM(total_stops) FROM marts.stops_by_mode").fetchone()[0]
total_modes = con.execute("SELECT COUNT(*) FROM marts.stops_by_mode").fetchone()[0]
total_routes = con.execute("SELECT COUNT(*) FROM staging.stg_routes").fetchone()[0]
central_stops = con.execute("SELECT COUNT(*) FROM marts.stops_central_helsinki").fetchone()[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Stops", f"{total_stops:,}")
col2.metric("Vehicle Modes", total_modes)
col3.metric("Active Routes", f"{total_routes:,}")
col4.metric("Central Stops (2km)", central_stops)

st.divider()

# Table
df = con.execute("SELECT * FROM marts.stops_by_mode").df()
st.dataframe(df, use_container_width=True)

# Chart
st.header("Stops per vehicle mode")
fig = px.bar(df, x="vehicle_mode", y="total_stops", color="vehicle_mode", text="total_stops")
st.plotly_chart(fig, use_container_width=True)

# Map
st.header("Stops Map — Central Helsinki (2km radius)")
map_df = con.execute("SELECT * FROM marts.stops_central_helsinki").df()
st.map(map_df, latitude="latitude", longitude="longitude", color="color", size=20)

# Footer
st.divider()
st.caption("Data source: HSL Digitransit API • Licensed under EUPL v1.2 / CC BY 4.0")