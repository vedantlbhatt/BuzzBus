import streamlit as st
import requests
from dotenv import load_dotenv
import os
from math import radians, sin, cos, sqrt, atan2

load_dotenv()

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

st.set_page_config(page_title="Georgia Tech Bus Route Finder", layout="centered", page_icon="🚌")

st.title("🚌 Georgia Tech Bus Route Finder")
st.markdown(
    """
    Use this app to discover the best bus routes between Georgia Tech buildings.
    Select your starting building and destination, then tap 'Find Best Bus Route' to get details.
    """
)

def haversine_distance(lat1, lon1, lat2, lon2):
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
        st.error(f"Failed to get routes. Status code: {response.status_code}")
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
        st.error(f"Failed to get vehicles. Status code: {response.status_code}")
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
    endpoint = "/GetRoutes"
    url = BASE_URL + endpoint
    params = {'APIKey': api_key, 'routeID': route_id}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to get route details. Status code: {response.status_code}")
        return None

def get_stops(api_key, route_id):
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
        st.error(f"Failed to get stops. Status code: {response.status_code}")
        return []

def get_stop_arrival_times(api_key, route_id=None, route_stop_id=None, times_per_stop=1):
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
        st.error(f"Failed to get arrival times. Status code: {response.status_code}")
        return None

with st.form(key="route_search_form"):
    col1, col2 = st.columns(2)
    with col1:
        begin_building = st.selectbox("Select Starting Building", list(BUILDINGS.keys()))
    with col2:
        dest_building = st.selectbox("Select Destination Building", list(BUILDINGS.keys()))
    search_button = st.form_submit_button(label="Find Best Bus Route")

result_heading_shown = False

if search_button:
    st.empty()  # clear any prior result heading before new search

    begin_point = BUILDINGS[begin_building]
    destination_point = BUILDINGS[dest_building]

    # Show loading message while searching
    with st.spinner(f"Searching routes from {begin_building} to {dest_building}..."):
        all_stops = []
        
        # Get all routes and filter to only active ones
        all_routes = get_all_routes(API_KEY)
        if all_routes:
            active_routes = filter_active_routes(all_routes, API_KEY)
            
            if not active_routes:
                st.warning("No buses are currently running.")
            else:
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

    st.markdown(f"### Searching routes from **{begin_building}** to **{dest_building}**...")
    result_heading_shown = True

if result_heading_shown:
    if route_costs:
        st.markdown("## Best Common Bus Routes (ranked by walking transfer distance)")
        for total_cost, route_id, begin_stop, dest_stop in route_costs:
            data = get_routes(API_KEY, route_id)
            if not data:
                continue

            dist_begin = haversine_distance(begin_stop[0], begin_stop[1], begin_point[0], begin_point[1])
            dist_dest = haversine_distance(dest_stop[0], dest_stop[1], destination_point[0], destination_point[1])

            with st.container():
                st.markdown("---")
                st.subheader(f"🚍 {data[0].get('Description', 'N/A')} (Route: {route_id})")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Start Stop:** {begin_stop[2]}")
                    st.markdown(f"**Distance to Start Point:** {dist_begin:.1f} meters")
                with col2:
                    st.markdown(f"**Destination Stop:** {dest_stop[2]}")
                    st.markdown(f"**Distance to Destination Point:** {dist_dest:.1f} meters")
    else:
        st.info("No common bus routes found between selected buildings.")
