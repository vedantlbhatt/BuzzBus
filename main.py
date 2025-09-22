import requests
from dotenv import load_dotenv
import os

load_dotenv()


API_KEY = os.getenv('TRANSLOC_API_KEY')
BASE_URL = os.getenv('TRANSLOC_BASE_URL')

def get_active_routes(api_key):
    endpoint = '/GetRoutesForMapWithScheduleWithEncodedLine'
    url = BASE_URL + endpoint
    params = {'APIKey': api_key}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        routes = response.json()
        print("Active routes:")
        for route in routes:
            print(f"RouteID: {route.get('RouteID')}, Description: {route.get('Description')}")
        return routes
    else:
        print(f"Failed to get routes. Status code: {response.status_code}")
        return None

def get_routes(api_key, route_id):
    endpoint = "/GetRoutes"
    url = BASE_URL + endpoint
    params = {'APIKey': api_key, 'routeID': route_id}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        route = response.json()
        for r in route:
            print(r.get('Description'))
        return route
    else:
        print(f"Failed to get routes. Status code: {response.status_code}")
        return None

def get_vehicle_points(api_key, route_id):
    endpoint = '/GetMapVehiclePoints'
    url = BASE_URL + endpoint
    params = {'APIKey': api_key, 'routeID': route_id}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        vehicles = response.json()
        if not vehicles:
            print(f"No vehicles found for route {route_id}.")
            return []
        print(f"Vehicles for RouteID {route_id}:")
        for vehicle in vehicles:
            lat = vehicle.get('Latitude')
            lng = vehicle.get('Longitude')
            print(f"(Route ID: {route_id}) Vehicle ID: {vehicle.get('VehicleID')} - Latitude: {lat}, Longitude: {lng}")
        return vehicles
    else:
        print(f"Failed to get vehicle points. Status code: {response.status_code}")
        return None

if __name__ == "__main__":
    routes = get_active_routes(API_KEY)
    if routes:
        # Select the first route (or any other as needed)2

        for route in routes:
            id = route.get('RouteID')
            curr_route = get_routes(API_KEY, id)
            get_vehicle_points(API_KEY, id)
