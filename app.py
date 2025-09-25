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
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


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
            return []
        return stops
    else:
        st.error(f"Failed to get stops. Status code: {response.status_code}")
        return []


# UI Controls
show_markdown = False

with st.form(key="route_search_form"):
    col1, col2 = st.columns(2)
    with col1:
        begin_building = st.selectbox("Select Starting Building", list(BUILDINGS.keys()))
    with col2:
        dest_building = st.selectbox("Select Destination Building", list(BUILDINGS.keys()))

    search_button = st.form_submit_button(label="Find Best Bus Route")

if search_button:
    begin_point = BUILDINGS[begin_building]
    destination_point = BUILDINGS[dest_building]
    show_markdown = True

    if show_markdown:
        st.markdown(f"### Searching routes from **{begin_building}** to **{dest_building}**...")

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

        # Sort stops by proximity to start and destination points
        begin_sorted_stops = sorted(
            all_stops,
            key=lambda stop: haversine_distance(stop[0], stop[1], begin_point[0], begin_point[1])
        )

        dest_sorted_stops = sorted(
            all_stops,
            key=lambda stop: haversine_distance(stop[0], stop[1], destination_point[0], destination_point[1])
        )

        visited_routes = set()
        common_routes = []
        route_stop_info = []
        count = 0
        max_len = max(len(begin_sorted_stops), len(dest_sorted_stops), 1)

        for i in range(max_len):
            if count >= 3:
                break
            route_begin = begin_sorted_stops[i][3]
            route_dest = dest_sorted_stops[i][3]
            if route_begin == route_dest and route_begin not in common_routes:
                common_routes.append(route_begin)
                route_stop_info.append((begin_sorted_stops[i], dest_sorted_stops[i]))
                count += 1
            else:
                if (route_begin, 1) in visited_routes and route_begin not in common_routes:
                    common_routes.append(route_begin)
                    route_stop_info.append((begin_sorted_stops[i], dest_sorted_stops[i]))
                    count += 1
                else:
                    visited_routes.add((route_begin, 0))
                if count >= 3:
                    break
                if (route_dest, 0) in visited_routes and route_dest not in common_routes:
                    common_routes.append(route_dest)
                    route_stop_info.append((begin_sorted_stops[i], dest_sorted_stops[i]))
                    count += 1
                else:
                    visited_routes.add((route_dest, 1))

        if common_routes:
            show_markdown = False
            st.markdown("## Best Common Bus Routes")
            for idx, route in enumerate(common_routes):
                data = get_routes(API_KEY, route)
                if data:
                    begin_stop = route_stop_info[idx][0]
                    dest_stop = route_stop_info[idx][1]

                    dist_begin = haversine_distance(begin_stop[0], begin_stop[1], begin_point[0], begin_point[1])
                    dist_dest = haversine_distance(dest_stop[0], dest_stop[1], destination_point[0], destination_point[1])

                    with st.container():
                        st.markdown("---")
                        st.subheader(f"🚍 {data[0].get('Description', 'N/A')} (Route: {route})")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Start Stop:** {begin_stop[2]}")
                            st.markdown(f"**Distance to Start Point:** {dist_begin:.1f} meters")
                        with col2:
                            st.markdown(f"**Destination Stop:** {dest_stop[2]}")
                            st.markdown(f"**Distance to Destination Point:** {dist_dest:.1f} meters")
        else:
            st.warning("No common routes found between the selected buildings.")
    else:
        st.error("Could not retrieve routes from the API. Please try again later.")
