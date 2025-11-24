"""Live test to verify whether vehicles on the same route share the same stops."""

import asyncio
import sys
import unittest
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Set

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.transloc_api_service import TranslocApiService  # noqa: E402


async def collect_vehicle_stop_differences() -> Dict[str, object]:
    """Fetch live data and determine if any vehicle pairs differ in served stops."""
    service = TranslocApiService()
    try:
        vehicles = await service.get_map_vehicle_points()

        vehicles_by_route: Dict[str, List[int]] = {}
        for vehicle in vehicles:
            route_id = service._extract_route_id(vehicle)
            if not route_id:
                continue
            vehicle_id = vehicle.get("VehicleID")
            if vehicle_id is None:
                continue
            try:
                vehicle_int = int(vehicle_id)
            except (TypeError, ValueError):
                continue

            vehicles_by_route.setdefault(route_id, []).append(vehicle_int)

        routes_with_multiple = {
            route_id: v_ids
            for route_id, v_ids in vehicles_by_route.items()
            if len(v_ids) > 1
        }

        differing_pairs: List[Dict[str, object]] = []

        for route_id, vehicle_ids in routes_with_multiple.items():
            arrival_times = await service.get_stop_arrival_times(route_id, times_per_stop=20)
            stops_by_vehicle: Dict[int, Set[str]] = {}

            for stop_entry in arrival_times:
                route_stop_id = stop_entry.get("RouteStopId") or stop_entry.get("RouteStopID")
                if route_stop_id is None:
                    continue
                route_stop_id = str(route_stop_id)

                for time_entry in stop_entry.get("Times", []):
                    vehicle_id = time_entry.get("VehicleId")
                    if vehicle_id is None:
                        continue
                    try:
                        vehicle_int = int(vehicle_id)
                    except (TypeError, ValueError):
                        continue
                    stops_by_vehicle.setdefault(vehicle_int, set()).add(route_stop_id)

            for vehicle_a, vehicle_b in combinations(sorted(stops_by_vehicle.keys()), 2):
                stops_a = stops_by_vehicle.get(vehicle_a, set())
                stops_b = stops_by_vehicle.get(vehicle_b, set())
                if stops_a != stops_b:
                    differing_pairs.append(
                        {
                            "route_id": route_id,
                            "vehicle_a": vehicle_a,
                            "vehicle_b": vehicle_b,
                            "only_a": sorted(list(stops_a - stops_b)),
                            "only_b": sorted(list(stops_b - stops_a)),
                        }
                    )

        return {
            "total_routes": len(vehicles_by_route),
            "routes_with_multiple": len(routes_with_multiple),
            "routes_inspected": sorted(routes_with_multiple.keys()),
            "differing_pairs": differing_pairs,
        }
    finally:
        await service.close()


class VehicleStopDifferenceTest(unittest.TestCase):
    """Unittest wrapper to surface vehicle stop differences quickly."""

    def test_vehicle_stop_sets_match(self) -> None:
        """Fail if any active vehicles on the same route serve different stop sets."""
        result = asyncio.run(collect_vehicle_stop_differences())

        if result["routes_with_multiple"] == 0:
            self.skipTest("No routes currently have multiple active vehicles to compare.")

        differing_pairs = result["differing_pairs"]

        if differing_pairs:
            details = [
                f"Route {pair['route_id']} vehicles {pair['vehicle_a']} vs {pair['vehicle_b']} "
                f"(only_a={len(pair['only_a'])}, only_b={len(pair['only_b'])})"
                for pair in differing_pairs
            ]
            self.fail(
                "Detected vehicles serving different stops:\n" + "\n".join(details)
            )

        self.assertFalse(differing_pairs, "Expected identical stop sets per route.")


if __name__ == "__main__":
    unittest.main()



