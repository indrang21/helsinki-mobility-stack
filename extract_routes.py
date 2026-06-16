import requests
import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

HSL_API_URL = "https://api.digitransit.fi/routing/v2/hsl/gtfs/v1"
API_KEY = os.getenv("HSL_API_KEY")

QUERY = """
{
  routes {
    gtfsId
    shortName
    longName
    mode
    type
    desc
  }
}
"""

def fetch_routes():
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
    
    if "errors" in result:
        print("GraphQL errors:", result["errors"])
        raise ValueError("API errors return korlo")
    
    return result

def save_to_file(data):
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/raw/hsl_routes_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filename

if __name__ == "__main__":
    print("HSL routes data fetch hochche...")
    data = fetch_routes()
    
    all_routes = data["data"]["routes"]
    print(f"✓ {len(all_routes)} ta route pawa gese")
    
    filename = save_to_file(data)
    print(f"✓ Save hoyeche: {filename}")
    
    print("\nFirst 5 routes:")
    for route in all_routes[:5]:
        print(f"  - {route['shortName']:5s} | {route['mode']:8s} | {route['longName']}")