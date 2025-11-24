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