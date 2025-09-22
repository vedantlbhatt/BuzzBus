import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('TRANSLOC_API_KEY')
BASE_URL = os.getenv('GT_TRANSLOC_BASE_URL')

BUILDINGS = {
    "Tech Tower": (33.772389, -84.394722),
    "Georgia Tech Library": (33.7743, -84.3956),
    "Clough Commons": (33.7747, -84.3963),
    "Hopkins Hall": (33.7760, -84.3993),
    "Folk Hall": (33.7726, -84.4032),
    "Montag Hall": (33.7736, -84.4012),
    "Student Center": (33.7744, -84.3987),
    "Campus Rec Center": (33.7735, -84.4036),
    "D.M. Smith": (33.7728, -84.3950),
    "Bobby Dodd Stadium": (33.7718, -84.3931),
}

def get_active_routes(api_key):
    endpoint = '/GetRoutesForMapWithScheduleWithEncodedLine'
    url = BASE_URL + endpoint
    params = {'APIKey': api_key}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to get routes. Status code: {response.status_code}")
        return None

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
            st.warning(f"No stops found for route {route_id}.")
            return []
        return stops
    else:
        st.error(f"Failed to get stops. Status code: {response.status_code}")
        return []

def haversine_distance(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2

    R = 6371000  # meters
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    c = 2*atan2(sqrt(a), sqrt(1 - a))
    return R*c

# Streamlit UI
st.title("Georgia Tech Bus Route Finder")

begin_building = st.selectbox("Select Starting Building", list(BUILDINGS.keys()))
dest_building = st.selectbox("Select Destination Building", list(BUILDINGS.keys()))

if st.button("Find Best Bus Route"):
    begin_point = BUILDINGS[begin_building]
    destination_point = BUILDINGS[dest_building]

    all_stops = []
    routes = get_active_routes(API_KEY)
    if routes:
        for route in routes:
            route_id = route.get('RouteID')
            stops = get_stops(API_KEY, route_id)
            if stops:
                for stop in stops:
                    stop_lat = stop.get('Latitude')
                    stop_lng = stop.get('Longitude')
                    stop_desc = stop.get('Description')
                    all_stops.append((stop_lat, stop_lng, stop_desc, route_id))

    begin_sorted_stops = sorted(
        all_stops,
        key=lambda stop: haversine_distance(stop[0], stop[1], begin_point[0], begin_point[1])
    )

    dest_sorted_stops = sorted(
        all_stops,
        key=lambda stop: haversine_distance(stop[0], stop[1], destination_point[0], destination_point[1])
    )

    found = False

    for lat, lng, desc, route in dest_sorted_stops:
        for latb, lngb, descb, routeb in begin_sorted_stops:
            if route == routeb:
                dist_dest = haversine_distance(lat, lng, destination_point[0], destination_point[1])
                dist_begin = haversine_distance(latb, lngb, begin_point[0], begin_point[1])
                data = get_routes(API_KEY, route)
                if data:
                    st.write(f"Route Description: {data[0].get('Description')}")
                st.write(f"Common Route: {route}")
                st.write(f"Start Stop: {descb}, Distance to Start Point: {dist_begin:.1f} meters")
                st.write(f"Destination Stop: {desc}, Distance to Destination Point: {dist_dest:.1f} meters")
                found = True
                break
        if found:
            break
    if not found:
        st.write("No common bus route found connecting these buildings.")
