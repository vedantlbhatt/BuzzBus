from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import os
from math import radians, sin, cos, sqrt, atan2

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

API_KEY = os.getenv('TRANSLOC_API_KEY')
BASE_URL = os.getenv('GT_TRANSLOC_BASE_URL')

BUILDINGS = {
    "Tech Tower": (33.7726510852488, -84.3947508475869),
    "Georgia Tech Library": (33.7747751124862, -84.39575939176652),
    "Clough Commons": (33.77532604620433, -84.39637188806334),
    "Hopkins Hall": (33.77850642030214, -84.39069072993782),
    "Glenn Hall": (33.77397354313724, -84.39167014943847),
    "North Ave East": (33.769581436909526, -84.39098961634303),
    "Student Center": (33.77361305511324, -84.39801594997785),
    "Campus Rec Center": (33.77559002203094, -84.40334559002532),
    "D.M. Smith": (33.77158232011701, -84.3911280052064),
    "Bobby Dodd Stadium": (33.772681846343005, -84.39323608111707),
}

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points on Earth."""
    R = 6371000  # meters
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def get_all_routes(api_key):
    """Get all routes from the system."""
    endpoint = '/GetRoutesForMapWithScheduleWithEncodedLine'
    url = BASE_URL + endpoint
    params = {'APIKey': api_key}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_active_vehicles(api_key, route_id=None):
    """Get vehicles currently on routes. Returns dict mapping route_id to list of vehicles."""
    endpoint = '/GetMapVehiclePoints'
    url = BASE_URL + endpoint
    params = {'APIKey': api_key}
    if route_id:
        params['routeID'] = route_id
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        vehicles = response.json()
        # Group vehicles by route
        route_vehicles = {}
        for vehicle in vehicles:
            rid = vehicle.get('RouteID')
            if rid:
                if rid not in route_vehicles:
                    route_vehicles[rid] = []
                route_vehicles[rid].append(vehicle)
        return route_vehicles
    else:
        return {}

def filter_active_routes(all_routes, api_key):
    """Filter routes to only those with active vehicles."""
    active_vehicle_routes = get_active_vehicles(api_key)
    
    # Filter routes that have vehicles currently on them
    active_routes = [
        route for route in all_routes 
        if route.get('RouteID') in active_vehicle_routes
    ]
    
    return active_routes

def get_routes(api_key, route_id):
    """Get specific route details."""
    endpoint = "/GetRoutes"
    url = BASE_URL + endpoint
    params = {'APIKey': api_key, 'routeID': route_id}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_stops(api_key, route_id):
    """Get stops for a specific route."""
    endpoint = '/GetStops'
    url = BASE_URL + endpoint
    params = {'APIKey': api_key, 'routeID': route_id}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        stops = response.json()
        if not stops:
            return []
        return stops
    else:
        return []

def get_stop_arrival_times(api_key, route_id=None, route_stop_id=None, times_per_stop=1):
    """Get arrival times for stops."""
    endpoint = '/GetStopArrivalTimes'
    url = BASE_URL + endpoint
    params = {
        'APIKey': api_key,
        'routeIDs': route_id,
        'routeStopIDs': route_stop_id,
        'timesPerStop': times_per_stop
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@app.route('/api/buildings', methods=['GET'])
def get_buildings():
    """Get list of available buildings."""
    return jsonify(list(BUILDINGS.keys()))

@app.route('/api/route-search', methods=['POST'])
def find_bus_routes():
    """Find best bus routes between two buildings or locations."""
    try:
        data = request.get_json()
        
        # Handle building-based search
        if 'begin_building' in data and 'dest_building' in data:
            begin_building = data.get('begin_building')
            dest_building = data.get('dest_building')
            
            if not begin_building or not dest_building:
                return jsonify({'error': 'Both begin_building and dest_building are required'}), 400
            
            if begin_building not in BUILDINGS or dest_building not in BUILDINGS:
                return jsonify({'error': 'Invalid building names'}), 400
            
            begin_point = BUILDINGS[begin_building]
            destination_point = BUILDINGS[dest_building]
            begin_name = begin_building
            dest_name = dest_building
            
        # Handle location-based search
        elif 'begin_coordinates' in data and 'dest_coordinates' in data:
            begin_coords = data.get('begin_coordinates')
            dest_coords = data.get('dest_coordinates')
            begin_location = data.get('begin_location', 'Starting Location')
            dest_location = data.get('dest_location', 'Destination Location')
            
            if not begin_coords or not dest_coords:
                return jsonify({'error': 'Both begin_coordinates and dest_coordinates are required'}), 400
            
            try:
                begin_lat, begin_lng = map(float, begin_coords.split(','))
                dest_lat, dest_lng = map(float, dest_coords.split(','))
                begin_point = (begin_lat, begin_lng)
                destination_point = (dest_lat, dest_lng)
                begin_name = begin_location
                dest_name = dest_location
            except ValueError:
                return jsonify({'error': 'Invalid coordinate format'}), 400
        else:
            return jsonify({'error': 'Invalid request format'}), 400
        
        all_stops = []
        
        # Get all routes and filter to only active ones
        all_routes = get_all_routes(API_KEY)
        if not all_routes:
            return jsonify({'error': 'Failed to get routes from API'}), 500
        
        active_routes = filter_active_routes(all_routes, API_KEY)
        
        if not active_routes:
            return jsonify({'routes': [], 'message': 'No buses are currently running.'})
        
        for route in active_routes:
            route_id = route.get('RouteID')
            stops = get_stops(API_KEY, route_id)
            if stops:
                for stop in stops:
                    stop_lat = stop.get('Latitude')
                    stop_lng = stop.get('Longitude')
                    stop_desc = stop.get('Description')
                    all_stops.append((stop_lat, stop_lng, stop_desc, route_id))

        nearby_start_routes = set(stop[3] for stop in all_stops)
        nearby_dest_routes = set(stop[3] for stop in all_stops)

        common_routes = list(nearby_start_routes.intersection(nearby_dest_routes))

        route_costs = []  # list of tuples (cost_meters, route_id, begin_stop, dest_stop)

        for route_id in common_routes:
            route_stops = [stop for stop in all_stops if stop[3] == route_id]
            if not route_stops:
                continue

            first_stop = min(
                route_stops,
                key=lambda stop: haversine_distance(stop[0], stop[1], begin_point[0], begin_point[1])
            )

            last_stop = min(
                route_stops,
                key=lambda stop: haversine_distance(stop[0], stop[1], destination_point[0], destination_point[1])
            )

            total_cost = (
                haversine_distance(first_stop[0], first_stop[1], begin_point[0], begin_point[1]) +
                haversine_distance(last_stop[0], last_stop[1], destination_point[0], destination_point[1])
            )

            route_costs.append((total_cost, route_id, first_stop, last_stop))

        # sort by total_cost ascending (best = shortest walking before/after bus)
        route_costs.sort(key=lambda x: x[0])

        MAX_DISPLAY = 5
        route_costs = route_costs[:MAX_DISPLAY]

        # Format results for frontend
        results = []
        for total_cost, route_id, begin_stop, dest_stop in route_costs:
            data = get_routes(API_KEY, route_id)
            if not data:
                continue

            dist_begin = haversine_distance(begin_stop[0], begin_stop[1], begin_point[0], begin_point[1])
            dist_dest = haversine_distance(dest_stop[0], dest_stop[1], destination_point[0], destination_point[1])

            results.append({
                'route_id': route_id,
                'route_name': data[0].get('Description', 'N/A'),
                'begin_stop': {
                    'name': begin_stop[2],
                    'distance': round(dist_begin, 1)
                },
                'dest_stop': {
                    'name': dest_stop[2],
                    'distance': round(dist_dest, 1)
                },
                'total_walking_distance': round(total_cost, 1)
            })

        return jsonify({
            'routes': results,
            'begin_building': begin_name,
            'dest_building': dest_name,
            'begin_location': begin_name,
            'dest_location': dest_name
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})

@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_from_directory('../static', 'index.html')

@app.route('/config.js')
def config():
    """Serve the config file."""
    return send_from_directory('../static', 'config.js')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
