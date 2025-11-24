#!/usr/bin/env python3
"""Test script for FastAPI backend endpoints."""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint."""
    print("Testing /api/health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ Health check passed")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_buildings():
    """Test buildings endpoint."""
    print("\nTesting /api/buildings...")
    try:
        response = requests.get(f"{BASE_URL}/api/buildings")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "Tech Tower" in data
        print(f"✓ Buildings endpoint passed ({len(data)} buildings)")
        return True
    except Exception as e:
        print(f"✗ Buildings endpoint failed: {e}")
        return False

def test_route_search_buildings():
    """Test route search with buildings."""
    print("\nTesting /api/RouteSearch (buildings)...")
    try:
        payload = {
            "begin_building": "Tech Tower",
            "dest_building": "Georgia Tech Library"
        }
        response = requests.post(f"{BASE_URL}/api/RouteSearch", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "routes" in data
        assert isinstance(data["routes"], list)
        assert "beginBuilding" in data or "begin_building" in data
        print(f"✓ Route search (buildings) passed - found {len(data['routes'])} routes")
        return True
    except Exception as e:
        print(f"✗ Route search (buildings) failed: {e}")
        print(f"  Response: {response.text if 'response' in locals() else 'No response'}")
        return False

def test_route_search_coordinates():
    """Test route search with coordinates."""
    print("\nTesting /api/RouteSearch (coordinates)...")
    try:
        payload = {
            "begin_location": "Tech Tower",
            "dest_location": "Library",
            "begin_coordinates": "33.7726510852488,-84.3947508475869",
            "dest_coordinates": "33.7747751124862,-84.39575939176652"
        }
        response = requests.post(f"{BASE_URL}/api/RouteSearch", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "routes" in data
        assert isinstance(data["routes"], list)
        print(f"✓ Route search (coordinates) passed - found {len(data['routes'])} routes")
        return True
    except Exception as e:
        print(f"✗ Route search (coordinates) failed: {e}")
        print(f"  Response: {response.text if 'response' in locals() else 'No response'}")
        return False

def test_map_routes():
    """Test map routes endpoint."""
    print("\nTesting /api/RouteSearch/map-routes...")
    try:
        response = requests.get(f"{BASE_URL}/api/RouteSearch/map-routes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Map routes endpoint passed - found {len(data)} routes")
        return True
    except Exception as e:
        print(f"✗ Map routes endpoint failed: {e}")
        return False

def test_map_vehicles():
    """Test map vehicles endpoint."""
    print("\nTesting /api/RouteSearch/map-vehicles...")
    try:
        response = requests.get(f"{BASE_URL}/api/RouteSearch/map-vehicles")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Map vehicles endpoint passed - found {len(data)} vehicles")
        return True
    except Exception as e:
        print(f"✗ Map vehicles endpoint failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("FastAPI Backend Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/api/health", timeout=2)
    except requests.exceptions.ConnectionError:
        print(f"\n✗ Cannot connect to {BASE_URL}")
        print("  Make sure the FastAPI server is running:")
        print("  cd backend && python -m uvicorn main:app --reload --port 5000")
        sys.exit(1)
    
    results = []
    results.append(test_health())
    results.append(test_buildings())
    results.append(test_route_search_buildings())
    results.append(test_route_search_coordinates())
    results.append(test_map_routes())
    results.append(test_map_vehicles())
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()

