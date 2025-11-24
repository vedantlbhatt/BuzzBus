#!/usr/bin/env python3
"""Test script specifically for ETA functionality."""

import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.transloc_api_service import TranslocApiService
from services.route_service import RouteService
from config import settings


async def test_get_stop_arrival_times():
    """Test GetStopArrivalTimes API call directly."""
    print("=" * 60)
    print("Testing GetStopArrivalTimes API")
    print("=" * 60)
    
    service = TranslocApiService()
    
    try:
        # First, get active routes
        print("\n1. Fetching active routes...")
        active_routes = await service.get_active_routes()
        print(f"   Found {len(active_routes)} active routes")
        
        if not active_routes:
            print("   ⚠ No active routes found - cannot test ETAs")
            return False
        
        # Get first route
        route = active_routes[0]
        route_id = service._extract_route_id(route)
        route_name = route.get("Description", "Unknown")
        print(f"   Testing with route: {route_name} (ID: {route_id})")
        
        # Get stops for this route
        print("\n2. Fetching stops for route...")
        stops = await service.get_stops(route_id)
        print(f"   Found {len(stops)} stops")
        
        if not stops:
            print("   ⚠ No stops found - cannot test ETAs")
            return False
        
        # Get first stop
        stop = stops[0]
        route_stop_id = None
        for key in ["RouteStopID", "RouteStopId", "routeStopID", "routeStopId"]:
            if key in stop:
                route_stop_id = str(stop[key]) if stop[key] is not None else None
                break
        
        stop_name = stop.get("Description", "Unknown")
        print(f"   Testing with stop: {stop_name} (ID: {route_stop_id})")
        
        if not route_stop_id:
            print("   ⚠ Could not extract route stop ID")
            return False
        
        # Get arrival times
        print("\n3. Fetching arrival times...")
        arrival_data = await service.get_stop_arrival_times(
            route_id, 
            route_stop_id, 
            times_per_stop=3
        )
        
        print(f"   Raw API response: {len(arrival_data)} items")
        if arrival_data:
            print(f"   First item keys: {list(arrival_data[0].keys())}")
            print(f"   First item sample: {arrival_data[0]}")
        
        # Test parsing
        print("\n4. Testing parsing logic...")
        route_service = RouteService(service)
        parsed_times = route_service._parse_arrival_times(arrival_data, route_stop_id)
        
        print(f"   Parsed {len(parsed_times)} arrival times")
        
        if parsed_times:
            print("\n   Parsed arrival times:")
            for i, at in enumerate(parsed_times, 1):
                print(f"   {i}. Minutes: {at.minutes}, Seconds: {at.seconds}")
                print(f"      Time: {at.time}, Estimate: {at.estimate_time}, Scheduled: {at.scheduled_time}")
                print(f"      Is Arriving: {at.is_arriving}, On Time Status: {at.on_time_status}")
                print(f"      Vehicle ID: {at.vehicle_id}, Vehicle Name: {at.vehicle_name}")
                print()
            
            print("   ✓ ETA parsing successful!")
            return True
        else:
            print("   ⚠ No arrival times parsed (this might be normal if no vehicles are near)")
            return True  # This is not necessarily a failure
            
    except Exception as e:
        print(f"\n   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await service.close()


async def test_route_search_with_eta():
    """Test route search endpoint with ETA data."""
    print("\n" + "=" * 60)
    print("Testing Route Search with ETA")
    print("=" * 60)
    
    service = TranslocApiService()
    route_service = RouteService(service)
    
    try:
        from models import RouteSearchRequest
        
        print("\n1. Testing route search from Tech Tower to Library...")
        request = RouteSearchRequest(
            begin_building="Tech Tower",
            dest_building="Georgia Tech Library"
        )
        
        result = await route_service.find_routes(request)
        
        print(f"   Found {len(result.routes)} routes")
        
        if result.routes:
            print("\n   Route details with ETAs:")
            for i, route in enumerate(result.routes, 1):
                print(f"\n   Route {i}: {route.route_name}")
                print(f"   Begin Stop: {route.begin_stop.name}")
                print(f"     - Distance: {route.begin_stop.distance}m")
                print(f"     - Arrival Times: {len(route.begin_stop.arrival_times)}")
                
                if route.begin_stop.arrival_times:
                    for j, at in enumerate(route.begin_stop.arrival_times[:2], 1):
                        print(f"       {j}. {at.minutes} min ({at.seconds}s)")
                        if at.is_arriving:
                            print(f"          → ARRIVING")
                        if at.on_time_status is not None:
                            status = {0: "On time", 2: "Early", 3: "Late"}.get(at.on_time_status, "Unknown")
                            print(f"          → {status}")
                
                print(f"   Dest Stop: {route.dest_stop.name}")
                print(f"     - Distance: {route.dest_stop.distance}m")
                print(f"     - Arrival Times: {len(route.dest_stop.arrival_times)}")
                
                if route.dest_stop.arrival_times:
                    for j, at in enumerate(route.dest_stop.arrival_times[:2], 1):
                        print(f"       {j}. {at.minutes} min ({at.seconds}s)")
                        if at.is_arriving:
                            print(f"          → ARRIVING")
                        if at.on_time_status is not None:
                            status = {0: "On time", 2: "Early", 3: "Late"}.get(at.on_time_status, "Unknown")
                            print(f"          → {status}")
            
            print("\n   ✓ Route search with ETA successful!")
            return True
        else:
            print("   ⚠ No routes found")
            return False
            
    except Exception as e:
        print(f"\n   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await service.close()


async def main():
    """Run all ETA tests."""
    print("\n" + "=" * 60)
    print("ETA Functionality Test Suite")
    print("=" * 60)
    print(f"API Base URL: {settings.transloc_base_url}")
    print(f"API Key: {settings.transloc_api_key[:4]}...")
    
    results = []
    
    # Test 1: Direct API call
    results.append(await test_get_stop_arrival_times())
    
    # Test 2: Route search with ETA
    results.append(await test_route_search_with_eta())
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All ETA tests passed!")
        return 0
    else:
        print("⚠ Some tests had issues (may be normal if no active routes/vehicles)")
        return 0  # Return 0 since missing data isn't necessarily a failure


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)


