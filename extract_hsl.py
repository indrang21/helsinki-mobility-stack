import requests
import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# .env file theke variables load koro
load_dotenv()

# HSL Digitransit GraphQL API endpoint
HSL_API_URL = "https://api.digitransit.fi/routing/v2/hsl/gtfs/v1"
API_KEY = os.getenv("HSL_API_KEY")

# GraphQL query: Helsinki-er sob bus/tram stops
QUERY = """
{
  stops {
    gtfsId
    name
    lat
    lon
    vehicleMode
  }
}
"""

def fetch_stops():
    """HSL API call kore stops data return kore"""
    if not API_KEY:
        raise ValueError("HSL_API_KEY .env file-e set kora hoyni!")
    
    headers = {
        "Content-Type": "application/json",
        "digitransit-subscription-key": API_KEY
    }
    response = requests.post(
        HSL_API_URL,
        json={"query": QUERY},
        headers=headers
    )
    response.raise_for_status()
    result = response.json()
    
    # GraphQL silent fail kore — errors field check kortei hobe
    if "errors" in result:
        print("GraphQL errors:", result["errors"])
        raise ValueError("API errors return korlo")
    
    return result

def save_to_file(data):
    """Data ke timestamped JSON file-e save kore"""
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/raw/hsl_stops_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filename

if __name__ == "__main__":
    print("HSL API theke data fetch hochche...")
    data = fetch_stops()
    
    all_stops = data["data"]["stops"]
    stops_count = len(all_stops)
    print(f"✓ {stops_count} ta stop pawa gese")
    
    # File-e save koro
    filename = save_to_file(data)
    print(f"✓ Save hoyeche: {filename}")
    
    # First 3 stops dekhao
    print("\nFirst 3 stops:")
    for stop in all_stops[:3]:
        print(f"  - {stop['name']} ({stop['vehicleMode']}) at {stop['lat']}, {stop['lon']}")