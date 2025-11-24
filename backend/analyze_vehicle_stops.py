#!/usr/bin/env python3
"""
Script to analyze if buses on the same route serve different stops.
Run this when multiple vehicles are active on the same route.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.transloc_api_service import TranslocApiService


async def analyze_vehicle_stop_differences():
    """Analyze all active vehicles to find routes where buses serve different stops."""
    transloc = TranslocApiService()
    
    print('=' * 80)
    print('VEHICLE STOP DIFFERENCE ANALYSIS')
    print('=' * 80)
    print()
    
    # Get all vehicles
    vehicles = await transloc.get_map_vehicle_points()
    print(f'Total active vehicles: {len(vehicles)}')
    
    # Group by route
    vehicles_by_route = {}
    for v in vehicles:
        route_id = transloc._extract_route_id(v)
        if route_id:
            if route_id not in vehicles_by_route:
                vehicles_by_route[route_id] = []
            vehicles_by_route[route_id].append({
                'id': v.get('VehicleID'),
                'name': v.get('Name')
            })
    
    print(f'Routes with active vehicles: {len(vehicles_by_route)}')
    print()
    
    # Find routes with multiple vehicles
    routes_with_multiple = {
        route_id: vehs 
        for route_id, vehs in vehicles_by_route.items() 
        if len(vehs) > 1
    }
    
    if not routes_with_multiple:
        print('⚠ No routes currently have multiple vehicles active.')
        print('  This analysis requires multiple vehicles on the same route.')
        print('  Run this script again when multiple buses are active on the same route.')
        await transloc.close()
        return
    
    print(f'Routes with multiple vehicles: {len(routes_with_multiple)}')
    for route_id, vehs in routes_with_multiple.items():
        print(f'  Route {route_id}: {len(vehs)} vehicles')
    print()
    
    # Analyze each route with multiple vehicles
    print('=' * 80)
    print('DETAILED ANALYSIS')
    print('=' * 80)
    print()
    
    routes_with_differences = []
    
    for route_id in sorted(routes_with_multiple.keys()):
        print(f'Route {route_id}:')
        print('-' * 80)
        
        # Get arrival times for this route
        arrival_times = await transloc.get_stop_arrival_times(route_id, times_per_stop=15)
        
        # Group stops by vehicle
        vehicle_stops = {}
        for stop_data in arrival_times:
            route_stop_id = str(stop_data.get('RouteStopId') or stop_data.get('RouteStopID') or '')
            stop_name = stop_data.get('StopDescription', 'Unknown')
            times = stop_data.get('Times', [])
            
            for time in times:
                vid = time.get('VehicleId')
                if vid:
                    vid_int = int(vid) if isinstance(vid, (int, float, str)) else vid
                    if vid_int not in vehicle_stops:
                        vehicle_stops[vid_int] = {}
                    vehicle_stops[vid_int][route_stop_id] = {
                        'name': stop_name,
                        'seconds': time.get('Seconds')
                    }
        
        vehicle_ids = sorted(vehicle_stops.keys())
        print(f'  Vehicles analyzed: {vehicle_ids}')
        print(f'  Total stops in route data: {len(arrival_times)}')
        print()
        
        # Compare vehicles pairwise
        route_has_differences = False
        
        for i in range(len(vehicle_ids)):
            for j in range(i + 1, len(vehicle_ids)):
                v1, v2 = vehicle_ids[i], vehicle_ids[j]
                stops1 = set(vehicle_stops[v1].keys())
                stops2 = set(vehicle_stops[v2].keys())
                
                print(f'  Vehicle {v1} vs Vehicle {v2}:')
                print(f'    Vehicle {v1}: {len(stops1)} stops')
                print(f'    Vehicle {v2}: {len(stops2)} stops')
                
                if stops1 != stops2:
                    route_has_differences = True
                    only_v1 = stops1 - stops2
                    only_v2 = stops2 - stops1
                    common = stops1 & stops2
                    
                    print(f'    ✗ DIFFERENT STOP SETS!')
                    print(f'    Common stops: {len(common)}')
                    print(f'    Only in Vehicle {v1}: {len(only_v1)} stops')
                    if only_v1:
                        v1_names = [vehicle_stops[v1][sid]['name'] for sid in sorted(list(only_v1))[:10]]
                        print(f'      Stops: {v1_names}')
                        if len(only_v1) > 10:
                            print(f'      ... and {len(only_v1) - 10} more')
                    print(f'    Only in Vehicle {v2}: {len(only_v2)} stops')
                    if only_v2:
                        v2_names = [vehicle_stops[v2][sid]['name'] for sid in sorted(list(only_v2))[:10]]
                        print(f'      Stops: {v2_names}')
                        if len(only_v2) > 10:
                            print(f'      ... and {len(only_v2) - 10} more')
                else:
                    print(f'    ✓ SAME STOP SETS ({len(stops1)} stops)')
                print()
        
        if route_has_differences:
            routes_with_differences.append(route_id)
    
    # Final summary
    print('=' * 80)
    print('SUMMARY')
    print('=' * 80)
    print(f'Routes with multiple vehicles: {len(routes_with_multiple)}')
    print(f'Routes where vehicles serve different stops: {len(routes_with_differences)}')
    print()
    
    if routes_with_differences:
        print('✓ ROUTES WITH DIFFERENCES:')
        for route_id in routes_with_differences:
            print(f'  - Route {route_id}')
        print()
        print('These routes have buses that serve different stops, likely due to:')
        print('  - Express vs local service')
        print('  - Route segments/branches')
        print('  - Different service patterns')
    elif routes_with_multiple:
        print('✓ All vehicles on the same route serve the same stops.')
    else:
        print('⚠ No routes with multiple vehicles found.')
        print('  Run this script again when multiple buses are active on the same route.')
    
    await transloc.close()


if __name__ == '__main__':
    asyncio.run(analyze_vehicle_stop_differences())

