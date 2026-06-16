import duckdb

con = duckdb.connect("helsinki.db")

# Query 1: Tram stops ki ki?
print("Top 10 tram stops:")
result = con.execute("""
    SELECT name, lat, lon 
    FROM raw.stops 
    WHERE vehicle_mode = 'TRAM' 
    LIMIT 10
""").fetchall()
for row in result:
    print(f"  {row[0]} → ({row[1]}, {row[2]})")

# Query 2: Duplicate names koto ase?
print("\nDuplicate stop names (top 10):")
result = con.execute("""
    SELECT name, COUNT(*) as count 
    FROM raw.stops 
    GROUP BY name 
    HAVING count > 1 
    ORDER BY count DESC 
    LIMIT 10
""").fetchall()
for name, count in result:
    print(f"  {name}: {count} times")

# Query 3: Helsinki center theke koto stops?
# Helsinki center: lat=60.1699, lon=24.9384
print("\nHelsinki center theke 1km-er moddhe stops:")
result = con.execute("""
    SELECT name, vehicle_mode,
           ROUND(SQRT(POW((lat - 60.1699) * 111, 2) + POW((lon - 24.9384) * 55, 2)) * 1000, 0) AS distance_m
    FROM raw.stops
    WHERE distance_m < 1000
    ORDER BY distance_m
    LIMIT 15
""").fetchall()
for name, mode, dist in result:
    print(f"  {name} ({mode}) — {dist}m")

con.close()