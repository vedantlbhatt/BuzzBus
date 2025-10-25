import requests

url = "https://m.gatech.edu/api/gtplaces/buildings/"

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    buildings = response.json()
    print(f"Got {len(buildings)} buildings")
except Exception as e:
    print("Error fetching buildings:", e)
