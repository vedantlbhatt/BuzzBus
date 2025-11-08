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

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (mapInstanceRef.current && vehicles.length > 0) {
      renderVehicles();
    }
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
    // Use production API URL when deployed
    const apiUrl = window.location.hostname === 'localhost'
      ? '/api/RouteSearch'
      : 'https://buzzbus-production.up.railway.app/api/RouteSearch';
    
    try {
      setLoading(true);
      
      const [routesResponse, vehiclesResponse] = await Promise.all([
        axios.get(`${apiUrl}/map-routes`),
        axios.get(`${apiUrl}/map-vehicles`)
      ]);

      // Only show routes that have active vehicles
      const allRoutes = routesResponse.data;
      const activeVehicles = vehiclesResponse.data;
      
      // Get route IDs that have active vehicles
      const activeRouteIds = new Set(activeVehicles.map(vehicle => vehicle.routeId));
      
      // Filter routes to only show active ones
      const activeRoutes = allRoutes.filter(route => activeRouteIds.has(route.routeId));
      
      setRoutes(activeRoutes);
      setVehicles(activeVehicles);

      // Set active routes as visible by default
      const defaultVisible = new Set(activeRoutes.map(route => route.routeId));
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

    vehicles.forEach(vehicle => {
      if (!vehicle.isOnRoute) return;

      const iconUrl = vehicle.isDelayed 
        ? 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" fill="#ff0000" stroke="#ffffff" stroke-width="2"/>
            <text x="12" y="16" text-anchor="middle" fill="white" font-size="12" font-weight="bold">🚌</text>
          </svg>
        `)
        : 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" fill="#4CAF50" stroke="#ffffff" stroke-width="2"/>
            <text x="12" y="16" text-anchor="middle" fill="white" font-size="12" font-weight="bold">🚌</text>
          </svg>
        `);

      const marker = new window.google.maps.Marker({
        position: { lat: vehicle.latitude, lng: vehicle.longitude },
        map: mapInstanceRef.current,
        title: `${vehicle.name} - Route ${vehicle.routeId}${vehicle.isDelayed ? ' (Delayed)' : ''}`,
        icon: {
          url: iconUrl,
          scaledSize: new window.google.maps.Size(24, 24),
          anchor: new window.google.maps.Point(12, 12)
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

  const toggleAllRoutes = () => {
    if (visibleRoutes.size === routes.length) {
      setVisibleRoutes(new Set());
    } else {
      setVisibleRoutes(new Set(routes.map(route => route.routeId)));
    }
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

  return (
    <div className="map-container">
      <div className="map-controls">
        <h2>🚌 Georgia Tech Bus Map</h2>
        <div className="controls-row">
          <button onClick={refreshData} className="refresh-button">
            🔄 Refresh Data
          </button>
          <button onClick={toggleAllRoutes} className="toggle-all-button">
            {visibleRoutes.size === routes.length ? 'Hide All Routes' : 'Show All Routes'}
          </button>
        </div>
        
        <div className="route-toggles">
          <h3>Route Controls</h3>
          {routes.map(route => (
            <label key={route.routeId} className="route-toggle">
              <input
                type="checkbox"
                checked={visibleRoutes.has(route.routeId)}
                onChange={() => toggleRoute(route.routeId)}
              />
              <span 
                className="route-color-indicator" 
                style={{ backgroundColor: route.mapLineColor }}
              ></span>
              {route.description}
            </label>
          ))}
        </div>

        <div className="map-legend">
          <h3>Legend</h3>
          <div className="legend-item">
            <span className="legend-icon">🚌</span>
            <span>Active Bus (On Time)</span>
          </div>
          <div className="legend-item">
            <span className="legend-icon" style={{ color: '#ff0000' }}>🚌</span>
            <span>Active Bus (Delayed)</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot"></span>
            <span>Bus Stop</span>
          </div>
        </div>
      </div>

      <div className="map-wrapper">
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
        <div ref={mapRef} className="map" />
      </div>
    </div>
  );
};

export default Map;
