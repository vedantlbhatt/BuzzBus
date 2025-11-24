import math
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import (
    Building, RouteSearchRequest, RouteSearchResponse, RouteResult,
    StopInfo, ArrivalTime, MapRoute, MapStop, MapVehicle, VehicleStop
)
from services.transloc_api_service import TranslocApiService


class RouteService:
    def __init__(self, transloc_api_service: TranslocApiService):
        self.transloc_api_service = transloc_api_service
        self.buildings = {
            "Tech Tower": Building(name="Tech Tower", latitude=33.7726510852488, longitude=-84.3947508475869),
            "Georgia Tech Library": Building(name="Georgia Tech Library", latitude=33.7747751124862, longitude=-84.39575939176652),
            "Clough Commons": Building(name="Clough Commons", latitude=33.77532604620433, longitude=-84.39637188806334),
            "Hopkins Hall": Building(name="Hopkins Hall", latitude=33.77850642030214, longitude=-84.39069072993782),
            "Glenn Hall": Building(name="Glenn Hall", latitude=33.77397354313724, longitude=-84.39167014943847),
            "North Ave East": Building(name="North Ave East", latitude=33.769581436909526, longitude=-84.39098961634303),
            "Student Center": Building(name="Student Center", latitude=33.77361305511324, longitude=-84.39801594997785),
            "Campus Rec Center": Building(name="Campus Rec Center", latitude=33.77559002203094, longitude=-84.40334559002532),
            "D.M. Smith": Building(name="D.M. Smith", latitude=33.77158232011701, longitude=-84.3911280052064),
            "Bobby Dodd Stadium": Building(name="Bobby Dodd Stadium", latitude=33.772681846343005, longitude=-84.39323608111707)
        }

    async def get_buildings(self) -> List[Building]:
        """Get list of all buildings."""
        return list(self.buildings.values())

    async def find_routes(self, request: RouteSearchRequest) -> RouteSearchResponse:
        """Find bus routes between two points."""
        begin_lat, begin_lng, begin_name = self._get_begin_point(request)
        dest_lat, dest_lng, dest_name = self._get_dest_point(request)

        all_stops: List[Tuple[float, float, str, str, Optional[str]]] = []

        # Get all routes and filter to only active ones
        active_routes = await self.transloc_api_service.get_active_routes()

        if not active_routes:
            return RouteSearchResponse(
                routes=[],
                begin_building=begin_name,
                dest_building=dest_name,
                begin_location=begin_name,
                dest_location=dest_name
            )

        # Extract route IDs
        route_ids = []
        for route in active_routes:
            route_id = self.transloc_api_service._extract_route_id(route)
            if route_id:
                route_ids.append(route_id)

        # Fetch all stops in parallel
        import asyncio
        stop_tasks = [self.transloc_api_service.get_stops(route_id) for route_id in route_ids]
        all_stops_lists = await asyncio.gather(*stop_tasks)

        for route_id, stops in zip(route_ids, all_stops_lists):
            for stop in stops:
                lat = stop.get("Latitude")
                lng = stop.get("Longitude")
                desc = stop.get("Description", "")
                route_stop_id = self._extract_route_stop_id(stop)
                
                if lat is not None and lng is not None:
                    all_stops.append((lat, lng, desc, route_id, route_stop_id))

        # Group stops by route
        stops_by_route: dict = {}
        for stop in all_stops:
            route_id = stop[3]
            if route_id not in stops_by_route:
                stops_by_route[route_id] = []
            stops_by_route[route_id].append(stop)

        route_costs: List[Tuple[float, str, Tuple, Tuple]] = []

        for route_id, route_stops in stops_by_route.items():
            if not route_stops:
                continue

            # Find the best start stop (closest to begin point)
            best_start_stop = min(
                route_stops,
                key=lambda s: self._haversine_distance(s[0], s[1], begin_lat, begin_lng)
            )
            start_walking_distance = self._haversine_distance(
                best_start_stop[0], best_start_stop[1], begin_lat, begin_lng
            )

            # Only consider routes where we don't have to walk too far to get to the bus
            max_start_walking_distance = 1000  # 1km max walking to bus
            if start_walking_distance > max_start_walking_distance:
                continue

            # Find the best destination stop (closest to destination point)
            best_dest_stop = min(
                route_stops,
                key=lambda s: self._haversine_distance(s[0], s[1], dest_lat, dest_lng)
            )
            dest_walking_distance = self._haversine_distance(
                best_dest_stop[0], best_dest_stop[1], dest_lat, dest_lng
            )

            # Only consider routes where we don't have to walk too far from the bus
            max_dest_walking_distance = 1000  # 1km max walking from bus
            if dest_walking_distance > max_dest_walking_distance:
                continue

            # Calculate total walking distance
            total_walking_distance = start_walking_distance + dest_walking_distance

            # Add penalty if start and dest stops are the same (not useful)
            if best_start_stop[2] == best_dest_stop[2]:
                total_walking_distance += 1000  # Heavy penalty for same stop

            route_costs.append((total_walking_distance, route_id, best_start_stop, best_dest_stop))

        route_costs.sort(key=lambda x: x[0])

        max_display = 5
        top_routes = route_costs[:max_display]

        # Fetch all route details and ETAs in parallel
        import asyncio
        
        async def empty_list():
            return []
        
        route_detail_tasks = []
        for total_cost, route_id, begin_stop, dest_stop in top_routes:
            route_details_task = self.transloc_api_service.get_route_details(route_id)
            begin_eta_task = (
                self.transloc_api_service.get_stop_arrival_times(route_id, begin_stop[4], 3)
                if begin_stop[4] else asyncio.create_task(empty_list())
            )
            dest_eta_task = (
                self.transloc_api_service.get_stop_arrival_times(route_id, dest_stop[4], 3)
                if dest_stop[4] else asyncio.create_task(empty_list())
            )
            route_detail_tasks.append((route_id, begin_stop, dest_stop, route_details_task, begin_eta_task, dest_eta_task))

        results = []
        for route_id, begin_stop, dest_stop, route_details_task, begin_eta_task, dest_eta_task in route_detail_tasks:
            route_details, begin_eta_data, dest_eta_data = await asyncio.gather(
                route_details_task, begin_eta_task, dest_eta_task
            )

            if not route_details:
                continue

            route_name = route_details[0].get("Description", "N/A")

            # Recalculate distances for consistency
            dist_begin = self._haversine_distance(begin_stop[0], begin_stop[1], begin_lat, begin_lng)
            dist_dest = self._haversine_distance(dest_stop[0], dest_stop[1], dest_lat, dest_lng)
            total_walking_distance = dist_begin + dist_dest

            # Parse arrival times for begin stop
            begin_arrival_times = self._parse_arrival_times(begin_eta_data, begin_stop[4])

            # Parse arrival times for dest stop
            dest_arrival_times = self._parse_arrival_times(dest_eta_data, dest_stop[4])

            results.append(
                RouteResult(
                    route_id=route_id,
                    route_name=route_name,
                    begin_stop=StopInfo(
                        name=begin_stop[2],
                        distance=round(dist_begin, 1),
                        route_stop_id=begin_stop[4],
                        arrival_times=begin_arrival_times
                    ),
                    dest_stop=StopInfo(
                        name=dest_stop[2],
                        distance=round(dist_dest, 1),
                        route_stop_id=dest_stop[4],
                        arrival_times=dest_arrival_times
                    ),
                    total_walking_distance=round(total_walking_distance, 1)
                )
            )

        return RouteSearchResponse(
            routes=results,
            begin_building=begin_name,
            dest_building=dest_name,
            begin_location=begin_name,
            dest_location=dest_name
        )

    def _get_begin_point(self, request: RouteSearchRequest) -> Tuple[float, float, str]:
        """Get begin point coordinates and name from request."""
        # Priority 1: If building name is explicitly provided, use building coordinates
        if request.begin_building and request.begin_building in self.buildings:
            building = self.buildings[request.begin_building]
            return (building.latitude, building.longitude, building.name)

        # Priority 2: If coordinates are provided (from Google Maps dropdown), use them
        if request.begin_coordinates:
            coords = request.begin_coordinates.split(',')
            if len(coords) == 2:
                try:
                    lat = float(coords[0].strip())
                    lng = float(coords[1].strip())
                    display_name = request.begin_location or "Starting Location"
                    
                    if request.begin_location:
                        # Try exact match first
                        exact_match = next(
                            (b for b in self.buildings.keys() 
                             if b.lower() == request.begin_location.lower()),
                            None
                        )
                        if exact_match:
                            display_name = exact_match
                        else:
                            # Try partial match
                            normalized_location = request.begin_location.lower().replace("avenue", "ave").replace("street", "st").replace("road", "rd").replace("boulevard", "blvd")
                            partial_match = next(
                                (b for b in self.buildings.keys() 
                                 if normalized_location in b.lower() or b.lower() in normalized_location),
                                None
                            )
                            if partial_match:
                                display_name = partial_match
                    
                    return (lat, lng, display_name)
                except ValueError:
                    pass

        # Priority 3: Try to match location name to a building
        if request.begin_location:
            # Try exact match
            exact_match = next(
                (b for b in self.buildings.keys() 
                 if b.lower() == request.begin_location.lower()),
                None
            )
            if exact_match:
                building = self.buildings[exact_match]
                return (building.latitude, building.longitude, building.name)

            # Try partial match
            normalized_location = request.begin_location.lower().replace("avenue", "ave").replace("street", "st").replace("road", "rd").replace("boulevard", "blvd")
            partial_match = next(
                (b for b in self.buildings.keys() 
                 if normalized_location in b.lower() or b.lower() in normalized_location),
                None
            )
            if partial_match:
                building = self.buildings[partial_match]
                return (building.latitude, building.longitude, building.name)

            # Fallback to Georgia Tech coordinates
            return (33.7756, -84.3963, request.begin_location)

        raise ValueError("Invalid begin point")

    def _get_dest_point(self, request: RouteSearchRequest) -> Tuple[float, float, str]:
        """Get destination point coordinates and name from request."""
        # Priority 1: If building name is explicitly provided, use building coordinates
        if request.dest_building and request.dest_building in self.buildings:
            building = self.buildings[request.dest_building]
            return (building.latitude, building.longitude, building.name)

        # Priority 2: If coordinates are provided (from Google Maps dropdown), use them
        if request.dest_coordinates:
            coords = request.dest_coordinates.split(',')
            if len(coords) == 2:
                try:
                    lat = float(coords[0].strip())
                    lng = float(coords[1].strip())
                    display_name = request.dest_location or "Destination Location"
                    
                    if request.dest_location:
                        # Try exact match first
                        exact_match = next(
                            (b for b in self.buildings.keys() 
                             if b.lower() == request.dest_location.lower()),
                            None
                        )
                        if exact_match:
                            display_name = exact_match
                        else:
                            # Try partial match
                            normalized_location = request.dest_location.lower().replace("avenue", "ave").replace("street", "st").replace("road", "rd").replace("boulevard", "blvd")
                            partial_match = next(
                                (b for b in self.buildings.keys() 
                                 if normalized_location in b.lower() or b.lower() in normalized_location),
                                None
                            )
                            if partial_match:
                                display_name = partial_match
                    
                    return (lat, lng, display_name)
                except ValueError:
                    pass

        # Priority 3: Try to match location name to a building
        if request.dest_location:
            # Try exact match
            exact_match = next(
                (b for b in self.buildings.keys() 
                 if b.lower() == request.dest_location.lower()),
                None
            )
            if exact_match:
                building = self.buildings[exact_match]
                return (building.latitude, building.longitude, building.name)

            # Try partial match
            normalized_location = request.dest_location.lower().replace("avenue", "ave").replace("street", "st").replace("road", "rd").replace("boulevard", "blvd")
            partial_match = next(
                (b for b in self.buildings.keys() 
                 if normalized_location in b.lower() or b.lower() in normalized_location),
                None
            )
            if partial_match:
                building = self.buildings[partial_match]
                return (building.latitude, building.longitude, building.name)

            # Fallback to Georgia Tech coordinates
            return (33.7756, -84.3963, request.dest_location)

        raise ValueError("Invalid destination point")

    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the great circle distance between two points on Earth in meters."""
        R = 6371000  # meters
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def _extract_route_stop_id(self, stop: dict) -> Optional[str]:
        """Extract route stop ID from stop object."""
        # Try both "RouteStopID" and "RouteStopId" (API uses different casing)
        route_stop_id = stop.get("RouteStopID") or stop.get("RouteStopId")
        if route_stop_id is None:
            return None
        if isinstance(route_stop_id, (int, float)):
            return str(int(route_stop_id))
        elif isinstance(route_stop_id, str):
            return route_stop_id
        return None

    def _parse_arrival_times(self, eta_data: List[dict], route_stop_id: Optional[str]) -> List[ArrivalTime]:
        """Parse arrival times from API response."""
        arrival_times = []
        if not eta_data or not route_stop_id:
            return arrival_times

        for eta_item in eta_data:
            stop_id = self._extract_route_stop_id(eta_item)
            if stop_id == route_stop_id and "ArrivalTimes" in eta_item:
                arrival_times_array = eta_item["ArrivalTimes"]
                if isinstance(arrival_times_array, list):
                    for arrival_time in arrival_times_array:
                        vehicle_id = arrival_time.get("VehicleID")
                        if vehicle_id is not None:
                            vehicle_id = str(vehicle_id) if not isinstance(vehicle_id, str) else vehicle_id
                        
                        arrival_time_obj = ArrivalTime(
                            minutes=arrival_time.get("Minutes"),
                            vehicle_id=vehicle_id,
                            vehicle_name=arrival_time.get("VehicleName")
                        )
                        arrival_times.append(arrival_time_obj)

        return arrival_times

    async def get_map_routes(self) -> List[MapRoute]:
        """Get routes with map information."""
        map_routes_data = await self.transloc_api_service.get_routes_for_map_with_schedule_with_encoded_line()
        result = []

        for route in map_routes_data:
            map_route = MapRoute(
                route_id=self.transloc_api_service._extract_route_id(route) or "",
                description=route.get("Description", ""),
                map_line_color=route.get("MapLineColor", "#000000"),
                map_latitude=route.get("MapLatitude", 0.0),
                map_longitude=route.get("MapLongitude", 0.0),
                map_zoom=route.get("MapZoom", 0),
                is_visible_on_map=route.get("IsVisibleOnMap", False),
                is_checked_on_map=route.get("IsCheckedOnMap", False),
                hide_route_line=route.get("HideRouteLine", False),
                encoded_polyline=route.get("EncodedPolyline", ""),
                stops=[]
            )

            # Get stops for this route
            if map_route.route_id:
                stops = await self.transloc_api_service.get_stops(map_route.route_id)
                for stop in stops:
                    map_stop = MapStop(
                        route_stop_id=self._extract_route_stop_id(stop) or "",
                        route_id=self.transloc_api_service._extract_route_id(stop) or "",
                        description=stop.get("Description", ""),
                        latitude=stop.get("Latitude", 0.0),
                        longitude=stop.get("Longitude", 0.0),
                        order=stop.get("Order", 0),
                        show_estimates_on_map=stop.get("ShowEstimatesOnMap", False),
                        show_defaulted_on_map=stop.get("ShowDefaultedOnMap", False)
                    )
                    map_route.stops.append(map_stop)

            result.append(map_route)

        return result

    async def get_map_vehicles(self) -> List[MapVehicle]:
        """Get vehicles for map display with their associated stops."""
        from models import VehicleStop
        
        vehicles_data = await self.transloc_api_service.get_map_vehicle_points()
        result = []

        # Group vehicles by route to fetch stop data efficiently
        vehicles_by_route: Dict[str, List[dict]] = {}
        for vehicle in vehicles_data:
            route_id = self.transloc_api_service._extract_route_id(vehicle)
            if route_id:
                if route_id not in vehicles_by_route:
                    vehicles_by_route[route_id] = []
                vehicles_by_route[route_id].append(vehicle)

        # For each route, get arrival times to determine which stops each vehicle serves
        vehicle_stops_map: Dict[int, List[dict]] = {}
        
        for route_id, route_vehicles in vehicles_by_route.items():
            # Get arrival times for all stops on this route
            arrival_times_data = await self.transloc_api_service.get_stop_arrival_times(
                route_id, times_per_stop=10
            )
            
            # Get all stops for this route to get coordinates
            all_stops = await self.transloc_api_service.get_stops(route_id)
            stops_by_id = {
                self._extract_route_stop_id(stop): stop 
                for stop in all_stops 
                if self._extract_route_stop_id(stop)
            }
            
            # Group stops by vehicle ID
            for stop_data in arrival_times_data:
                route_stop_id = self._extract_route_stop_id(stop_data)
                stop_info = stops_by_id.get(route_stop_id, {})
                stop_name = stop_data.get("StopDescription", stop_info.get("Description", ""))
                
                times = stop_data.get("Times", [])
                for time in times:
                    vehicle_id = time.get("VehicleId")
                    if vehicle_id is not None:
                        vehicle_id_int = int(vehicle_id) if isinstance(vehicle_id, (int, float, str)) else vehicle_id
                        if vehicle_id_int not in vehicle_stops_map:
                            vehicle_stops_map[vehicle_id_int] = []
                        
                        vehicle_stops_map[vehicle_id_int].append({
                            "route_stop_id": str(route_stop_id) if route_stop_id else "",
                            "stop_name": stop_name,
                            "latitude": stop_info.get("Latitude", 0.0),
                            "longitude": stop_info.get("Longitude", 0.0),
                            "arrival_seconds": time.get("Seconds")
                        })

        # Build MapVehicle objects with stop information
        for vehicle in vehicles_data:
            vehicle_id = vehicle.get("VehicleID")
            vehicle_id_int = int(vehicle_id) if vehicle_id is not None and isinstance(vehicle_id, (int, float, str)) else None
            
            # Get stops for this vehicle
            vehicle_stops = vehicle_stops_map.get(vehicle_id_int, []) if vehicle_id_int else []
            
            map_vehicle = MapVehicle(
                vehicle_id=str(vehicle_id) if vehicle_id is not None else "",
                route_id=self.transloc_api_service._extract_route_id(vehicle) or "",
                name=vehicle.get("Name", ""),
                latitude=vehicle.get("Latitude", 0.0),
                longitude=vehicle.get("Longitude", 0.0),
                ground_speed=vehicle.get("GroundSpeed", 0.0),
                heading=vehicle.get("Heading", 0.0),
                seconds=vehicle.get("Seconds", 0),
                is_on_route=vehicle.get("IsOnRoute", False),
                is_delayed=vehicle.get("IsDelayed", False),
                stops=[
                    VehicleStop(
                        route_stop_id=stop["route_stop_id"],
                        stop_name=stop["stop_name"],
                        latitude=stop["latitude"],
                        longitude=stop["longitude"],
                        arrival_seconds=stop.get("arrival_seconds")
                    )
                    for stop in vehicle_stops
                ]
            )
            result.append(map_vehicle)

        return result

