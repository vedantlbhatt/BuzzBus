import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';

const Map = () => {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const polylinesRef = useRef([]);
  const markersRef = useRef([]);
  const [routes, setRoutes] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [visibleRoutes, setVisibleRoutes] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isGoogleMapsLoaded, setIsGoogleMapsLoaded] = useState(false);

  // Georgia Tech coordinates
  const GT_CENTER = { lat: 33.7756, lng: -84.3963 };
  const GT_BOUNDS = {
    north: 33.7856,
    south: 33.7656,
    east: -84.3863,
    west: -84.4063
  };

  useEffect(() => {
    // Check if Google Maps API is loaded
    if (window.google && window.google.maps) {
      setIsGoogleMapsLoaded(true);
    } else {
      // Wait for Google Maps API to load
      const checkGoogleMaps = setInterval(() => {
        if (window.google && window.google.maps) {
          setIsGoogleMapsLoaded(true);
          clearInterval(checkGoogleMaps);
        }
      }, 100);

      return () => clearInterval(checkGoogleMaps);
    }
  }, []);

  useEffect(() => {
    if (isGoogleMapsLoaded) {
      initializeMap();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isGoogleMapsLoaded]);

  useEffect(() => {
    if (mapInstanceRef.current && routes.length > 0) {
      renderRoutes();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [routes, visibleRoutes]);

  useEffect(() => {
    if (mapInstanceRef.current && vehicles.length > 0) {
      renderVehicles();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vehicles]);

  const initializeMap = () => {
    if (!mapRef.current) return;

    mapInstanceRef.current = new window.google.maps.Map(mapRef.current, {
      center: GT_CENTER,
      zoom: 15,
      mapTypeId: window.google.maps.MapTypeId.ROADMAP,
      styles: [
        {
          featureType: 'poi',
          elementType: 'labels',
          stylers: [{ visibility: 'off' }]
        }
      ]
    });

    // Set bounds to Georgia Tech area
    mapInstanceRef.current.fitBounds(new window.google.maps.LatLngBounds(
      new window.google.maps.LatLng(GT_BOUNDS.south, GT_BOUNDS.west),
      new window.google.maps.LatLng(GT_BOUNDS.north, GT_BOUNDS.east)
    ));

    loadMapData();
  };

  const loadMapData = async () => {
    // Determine API URL based on environment
    const apiUrl = (() => {
      const hostname = window.location.hostname;
      // Local development - use proxy
      if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return '/api/RouteSearch';
      }
      // Production - use Railway backend
      return 'https://buzzbus-production.up.railway.app/api/RouteSearch';
    })();
    
    try {
      setLoading(true);
      
      const [routesResponse, vehiclesResponse] = await Promise.all([
        axios.get(`${apiUrl}/map-routes`),
        axios.get(`${apiUrl}/map-vehicles`)
      ]);

      const allRoutes = routesResponse.data;
      const activeVehicles = vehiclesResponse.data;
      
      // Get route IDs that have active vehicles
      const activeRouteIds = new Set(activeVehicles.map(vehicle => vehicle.routeId).filter(id => id));
      
      // Filter routes to only show active ones
      const activeRoutes = allRoutes.filter(route => route.routeId && activeRouteIds.has(route.routeId));
      
      setRoutes(activeRoutes);
      setVehicles(activeVehicles);

      // Set active routes as visible by default (filter out falsy IDs)
      const defaultVisible = new Set(activeRoutes.map(route => route.routeId).filter(id => id));
      setVisibleRoutes(defaultVisible);

    } catch (err) {
      setError(`Failed to load map data: ${err.message || 'Unknown error'}`);
      console.error('Error loading map data:', err);
      console.error('API URL:', apiUrl);
      console.error('Response:', err.response);
      console.error('Error details:', err.response?.data);
    } finally {
      setLoading(false);
    }
  };

  const renderRoutes = () => {
    // Clear existing polylines
    polylinesRef.current.forEach(polyline => polyline.setMap(null));
    polylinesRef.current = [];

    routes.forEach(route => {
      if (!visibleRoutes.has(route.routeId)) return;

      // Create polyline from encoded polyline if available
      if (route.encodedPolyline) {
        try {
          const decodedPath = window.google.maps.geometry.encoding.decodePath(route.encodedPolyline);
          const polyline = new window.google.maps.Polyline({
            path: decodedPath,
            geodesic: true,
            strokeColor: route.mapLineColor || '#000000',
            strokeOpacity: 0.8,
            strokeWeight: 4
          });
          polyline.setMap(mapInstanceRef.current);
          polylinesRef.current.push(polyline);
        } catch (err) {
          console.warn(`Failed to decode polyline for route ${route.routeId}:`, err);
        }
      }

      // Add stop markers
      route.stops.forEach(stop => {
        if (stop.showDefaultedOnMap) {
          const marker = new window.google.maps.Marker({
            position: { lat: stop.latitude, lng: stop.longitude },
            map: mapInstanceRef.current,
            title: stop.description,
            icon: {
              path: window.google.maps.SymbolPath.CIRCLE,
              scale: 6,
              fillColor: route.mapLineColor || '#000000',
              fillOpacity: 1,
              strokeColor: '#ffffff',
              strokeWeight: 2
            }
          });
          markersRef.current.push(marker);
        }
      });
    });
  };

  const renderVehicles = () => {
    // Clear existing vehicle markers
    markersRef.current.forEach(marker => marker.setMap(null));
    markersRef.current = [];

    // Create a map of routeId to color
    const routeColorMap = {};
    routes.forEach(route => {
      if (route.routeId) {
        routeColorMap[route.routeId] = route.mapLineColor || '#6366f1';
      }
    });

    vehicles.forEach(vehicle => {
      if (!vehicle.isOnRoute) return;

      // Get route color, default to gray if not found
      const routeColor = routeColorMap[vehicle.routeId] || '#808080';
      
      // Get heading in degrees (0-360), default to 0 if not available
      const heading = vehicle.heading || 0;
      
      // Convert heading to rotation (Google Maps uses degrees clockwise from north)
      // SVG rotation is clockwise, so we can use heading directly
      const rotation = heading;
      
      // Create triangle pointing in direction of travel
      // Triangle points upward (north) by default, then rotated by heading
      const iconUrl = 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
        <svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
          <g transform="translate(10,10) rotate(${rotation}) translate(-10,-10)">
            <path d="M 10 2 L 18 18 L 2 18 Z" fill="${routeColor}" stroke="#ffffff" stroke-width="1.5" stroke-linejoin="round"/>
          </g>
        </svg>
      `);

      const marker = new window.google.maps.Marker({
        position: { lat: vehicle.latitude, lng: vehicle.longitude },
        map: mapInstanceRef.current,
        title: `${vehicle.name} - Route ${vehicle.routeId}${vehicle.isDelayed ? ' (Delayed)' : ''}`,
        icon: {
          url: iconUrl,
          scaledSize: new window.google.maps.Size(20, 20),
          anchor: new window.google.maps.Point(10, 10),
          rotation: 0  // Rotation handled in SVG
        }
      });

      // Add info window
      const infoWindow = new window.google.maps.InfoWindow({
        content: `
          <div style="padding: 8px;">
            <h3 style="margin: 0 0 4px 0; font-size: 14px;">${vehicle.name}</h3>
            <p style="margin: 0; font-size: 12px;">Route: ${vehicle.routeId}</p>
            <p style="margin: 0; font-size: 12px;">Speed: ${Math.round(vehicle.groundSpeed)} mph</p>
            <p style="margin: 0; font-size: 12px;">Status: ${vehicle.isDelayed ? 'Delayed' : 'On Time'}</p>
            <p style="margin: 0; font-size: 12px;">Last Update: ${vehicle.seconds}s ago</p>
          </div>
        `
      });

      marker.addListener('click', () => {
        infoWindow.open(mapInstanceRef.current, marker);
      });

      markersRef.current.push(marker);
    });
  };

  const toggleRoute = (routeId) => {
    const newVisibleRoutes = new Set(visibleRoutes);
    if (newVisibleRoutes.has(routeId)) {
      newVisibleRoutes.delete(routeId);
    } else {
      newVisibleRoutes.add(routeId);
    }
    setVisibleRoutes(newVisibleRoutes);
  };

  const refreshData = () => {
    loadMapData();
  };

  if (!isGoogleMapsLoaded) {
    return (
      <div className="map-loading">
        <p>Loading Google Maps...</p>
      </div>
    );
  }

  // Count vehicles per route
  const routeVehicleCounts = {};
  vehicles.forEach(vehicle => {
    if (vehicle.routeId) {
      routeVehicleCounts[vehicle.routeId] = (routeVehicleCounts[vehicle.routeId] || 0) + 1;
    }
  });

  // Get unique routes with their vehicle counts
  const activeRoutesData = routes.map(route => ({
    routeId: route.routeId,
    description: route.description || route.routeName || `Route ${route.routeId}`,
    color: route.mapLineColor || '#6366f1',
    vehicleCount: routeVehicleCounts[route.routeId] || 0
  }));

  // Determine route color name
  const getRouteColorName = (description, color) => {
    const descUpper = (description || '').toUpperCase();
    if (descUpper.includes('RED')) return 'RED';
    if (descUpper.includes('BLUE')) return 'BLUE';
    if (descUpper.includes('TROLLEY') || descUpper.includes('YELLOW')) return 'TROLLEY';
    return 'ROUTE';
  };

  return (
    <div className="map-view-container">
      <div className="map-view-content">
        {/* Map Container */}
        <div className="map-display-container">
          {loading && (
            <div className="map-loading-overlay">
              <p>Loading map data...</p>
            </div>
          )}
          {error && (
            <div className="map-error">
              <p>{error}</p>
              <button onClick={refreshData}>Retry</button>
            </div>
          )}
          <div ref={mapRef} className="map-display" />
          {!mapInstanceRef.current && (
            <div className="map-placeholder">
              <div className="map-placeholder-content">
                <div className="map-placeholder-title">CAMPUS MAP</div>
                <div className="map-placeholder-subtitle">Real-time vehicle tracking</div>
              </div>
              {/* Decorative grid */}
              <div className="map-grid-overlay"></div>
            </div>
          )}
        </div>

        {/* Active Routes Section */}
        <div className="active-routes-section">
          <div className="active-routes-header">ACTIVE ROUTES</div>
          <div className="active-routes-grid">
            {activeRoutesData.map((routeData, index) => {
              const routeColorName = getRouteColorName(routeData.description, routeData.color);
              const isFirstCard = index === 0;
              const routeColor = routeData.color || '#6366f1';
              
              // Determine if route color is red, blue, or other
              const isRed = routeColorName === 'RED';
              const isBlue = routeColorName === 'BLUE';
              const isTrolley = routeColorName === 'TROLLEY';
              
              return (
                <div
                  key={routeData.routeId}
                  className={`active-route-card ${isFirstCard ? 'active-route-card-dark' : 'active-route-card-light'}`}
                  onClick={() => toggleRoute(routeData.routeId)}
                >
                  <div className="active-route-header">
                    <div
                      className="active-route-indicator"
                      style={{
                        backgroundColor: isRed ? '#dc2626' : isBlue ? '#2563eb' : isTrolley ? '#eab308' : routeColor,
                        borderColor: isFirstCard ? '#ffffff' : '#1e293b'
                      }}
                    ></div>
                    <div className={`active-route-name ${isFirstCard ? 'active-route-name-dark' : 'active-route-name-light'}`}>
                      {routeColorName}
                    </div>
                  </div>
                  <div className={`active-route-count ${isFirstCard ? 'active-route-count-dark' : 'active-route-count-light'}`}>
                    {routeData.vehicleCount}
                  </div>
                  <div className={`active-route-status ${isFirstCard ? 'active-route-status-dark' : 'active-route-status-light'}`}>
                    BUSES RUNNING
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Map;
