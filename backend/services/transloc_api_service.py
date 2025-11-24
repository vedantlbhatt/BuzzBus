import httpx
import logging
import sys
from pathlib import Path
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings

logger = logging.getLogger(__name__)


class TranslocApiService:
    def __init__(self):
        self.base_url = settings.transloc_base_url
        self.api_key = settings.transloc_api_key
        self.client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
        )

    async def get_all_routes(self) -> List[dict]:
        """Get all routes from the Transloc API."""
        endpoint = "/GetRoutes"
        url = f"{self.base_url}{endpoint}"
        params = {"APIKey": self.api_key}
        
        try:
            response = await self.client.get(url, params=params)
            if response.is_success:
                return response.json() or []
            else:
                logger.error(f"TransLoc API error: {response.status_code} - {response.reason_phrase}")
                return []
        except Exception as ex:
            logger.error(f"TransLoc API exception: {ex}")
            return []

    async def get_active_routes(self) -> List[dict]:
        """Get only routes that currently have active vehicles."""
        all_routes = await self.get_all_routes()
        active_vehicles = await self.get_active_vehicles()
        
        active_route_ids = set(active_vehicles.keys())
        
        active_routes = []
        for route in all_routes:
            route_id = self._extract_route_id(route)
            if route_id and route_id in active_route_ids:
                active_routes.append(route)
        
        return active_routes

    async def get_stops(self, route_id: str) -> List[dict]:
        """Get stops for a specific route."""
        endpoint = "/GetStops"
        url = f"{self.base_url}{endpoint}"
        params = {"APIKey": self.api_key, "routeID": route_id}
        
        try:
            response = await self.client.get(url, params=params)
            if response.is_success:
                return response.json() or []
            else:
                logger.error(f"TransLoc API error for stops: {response.status_code} - {response.reason_phrase}")
                return []
        except Exception as ex:
            logger.error(f"TransLoc API exception for stops: {ex}")
            return []

    async def get_route_details(self, route_id: str) -> List[dict]:
        """Get detailed information about a specific route."""
        endpoint = "/GetRoutes"
        url = f"{self.base_url}{endpoint}"
        params = {"APIKey": self.api_key, "routeID": route_id}
        
        try:
            response = await self.client.get(url, params=params)
            if response.is_success:
                return response.json() or []
            else:
                logger.error(f"TransLoc API error for route details: {response.status_code} - {response.reason_phrase}")
                return []
        except Exception as ex:
            logger.error(f"TransLoc API exception for route details: {ex}")
            return []

    async def get_active_vehicles(self) -> Dict[str, List[dict]]:
        """Get all active vehicles, grouped by route ID."""
        endpoint = "/GetMapVehiclePoints"
        url = f"{self.base_url}{endpoint}"
        params = {"APIKey": self.api_key}
        
        try:
            response = await self.client.get(url, params=params)
            if response.is_success:
                vehicles = response.json() or []
                
                route_vehicles: Dict[str, List[dict]] = {}
                for vehicle in vehicles:
                    route_id = self._extract_route_id(vehicle)
                    if route_id:
                        if route_id not in route_vehicles:
                            route_vehicles[route_id] = []
                        route_vehicles[route_id].append(vehicle)
                
                return route_vehicles
            else:
                logger.error(f"TransLoc API error: {response.status_code} - {response.reason_phrase}")
                return {}
        except Exception as ex:
            logger.error(f"TransLoc API exception: {ex}")
            return {}

    async def get_routes_for_map_with_schedule_with_encoded_line(self) -> List[dict]:
        """Get routes with schedule and encoded polyline for map display."""
        endpoint = "/GetRoutesForMapWithScheduleWithEncodedLine"
        url = f"{self.base_url}{endpoint}"
        params = {"APIKey": self.api_key}
        
        try:
            response = await self.client.get(url, params=params)
            if response.is_success:
                return response.json() or []
            else:
                logger.error(f"TransLoc API error for map routes: {response.status_code} - {response.reason_phrase}")
                return []
        except Exception as ex:
            logger.error(f"TransLoc API exception for map routes: {ex}")
            return []

    async def get_map_vehicle_points(self) -> List[dict]:
        """Get current vehicle positions for map display."""
        endpoint = "/GetMapVehiclePoints"
        url = f"{self.base_url}{endpoint}"
        params = {"APIKey": self.api_key}
        
        try:
            response = await self.client.get(url, params=params)
            if response.is_success:
                return response.json() or []
            else:
                logger.error(f"TransLoc API error for vehicle points: {response.status_code} - {response.reason_phrase}")
                return []
        except Exception as ex:
            logger.error(f"TransLoc API exception for vehicle points: {ex}")
            return []

    async def get_stop_arrival_times(
        self, 
        route_id: str, 
        route_stop_id: Optional[str] = None, 
        times_per_stop: int = 1
    ) -> List[dict]:
        """Get arrival times for stops."""
        endpoint = "/GetStopArrivalTimes"
        url = f"{self.base_url}{endpoint}"
        params = {
            "APIKey": self.api_key,
            "routeIDs": route_id,
            "timesPerStop": times_per_stop
        }
        
        if route_stop_id:
            params["routeStopIDs"] = route_stop_id
        
        try:
            response = await self.client.get(url, params=params)
            if response.is_success:
                return response.json() or []
            else:
                logger.error(f"TransLoc API error for arrival times: {response.status_code} - {response.reason_phrase}")
                return []
        except Exception as ex:
            logger.error(f"TransLoc API exception for arrival times: {ex}")
            return []

    def _extract_route_id(self, obj: dict) -> Optional[str]:
        """Extract route ID from an object, handling both string and numeric IDs."""
        route_id = obj.get("RouteID")
        if route_id is None:
            return None
        
        if isinstance(route_id, (int, float)):
            return str(int(route_id))
        elif isinstance(route_id, str):
            return route_id
        else:
            return None

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

