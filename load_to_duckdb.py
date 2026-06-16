import duckdb
import json
import glob
from pathlib import Path

DB_PATH = "helsinki.db"
RAW_DATA_PATH = "data/raw"

def get_latest_file(prefix):
    """Latest file with given prefix khujo"""
    files = glob.glob(f"{RAW_DATA_PATH}/{prefix}_*.json")
    if not files:
        raise FileNotFoundError(f"No {prefix} files found in {RAW_DATA_PATH}/")
    return max(files)

def load_stops(con):
    """Stops JSON theke raw.stops table banao"""
    latest = get_latest_file("hsl_stops")
    print(f"Loading stops from: {latest}")
    
    with open(latest, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    stops = data["data"]["stops"]
    
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    con.execute("DROP TABLE IF EXISTS raw.stops")
    
    con.execute("""
        CREATE TABLE raw.stops AS
        SELECT 
            gtfsId AS gtfs_id,
            name,
            lat,
            lon,
            vehicleMode AS vehicle_mode,
            CURRENT_TIMESTAMP AS loaded_at
        FROM (SELECT UNNEST(?::JSON[]) AS stop_data)
        , LATERAL (
            SELECT 
                stop_data->>'gtfsId' AS gtfsId,
                stop_data->>'name' AS name,
                CAST(stop_data->>'lat' AS DOUBLE) AS lat,
                CAST(stop_data->>'lon' AS DOUBLE) AS lon,
                stop_data->>'vehicleMode' AS vehicleMode
        )
    """, [json.dumps(stops)])
    
    count = con.execute("SELECT COUNT(*) FROM raw.stops").fetchone()[0]
    print(f"✓ {count} stops loaded into raw.stops")

def load_routes(con):
    """Routes JSON theke raw.routes table banao"""
    latest = get_latest_file("hsl_routes")
    print(f"Loading routes from: {latest}")
    
    with open(latest, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    routes = data["data"]["routes"]
    
    con.execute("DROP TABLE IF EXISTS raw.routes")
    
    con.execute("""
        CREATE TABLE raw.routes AS
        SELECT 
            gtfsId AS gtfs_id,
            shortName AS short_name,
            longName AS long_name,
            mode,
            type,
            "desc" AS description,
            CURRENT_TIMESTAMP AS loaded_at
        FROM (SELECT UNNEST(?::JSON[]) AS route_data)
        , LATERAL (
            SELECT 
                route_data->>'gtfsId' AS gtfsId,
                route_data->>'shortName' AS shortName,
                route_data->>'longName' AS longName,
                route_data->>'mode' AS mode,
                CAST(route_data->>'type' AS INTEGER) AS type,
                route_data->>'desc' AS "desc"
        )
    """, [json.dumps(routes)])
    
    count = con.execute("SELECT COUNT(*) FROM raw.routes").fetchone()[0]
    print(f"✓ {count} routes loaded into raw.routes")

if __name__ == "__main__":
    print("DuckDB-e load shuru...\n")
    con = duckdb.connect(DB_PATH)
    
    load_stops(con)
    print()
    load_routes(con)
    
    con.close()
    print("\n✓ All loads complete!")