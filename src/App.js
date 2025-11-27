import React, { useState, useCallback } from 'react';
import axios from 'axios';
import PlaceAutocomplete from './components/PlaceAutocomplete';
import Map from './components/Map';
import './App.css';

const resolvePlaceCoordinates = async (place) => {
  if (!place || !place.name) {
    return place;
  }

  // If this place was selected from dropdown, use it as-is
  if (place.fromAutocomplete === true && place.coordinates) {
    return place;
  }

  if (!(window.google && window.google.maps && window.google.maps.places)) {
    return place;
  }

  const autocompleteService = new window.google.maps.places.AutocompleteService();
  
  // Atlanta bounds
  const atlantaBounds = new window.google.maps.LatLngBounds(
    new window.google.maps.LatLng(33.6, -84.5),  // Southwest
    new window.google.maps.LatLng(33.9, -84.3)    // Northeast
  );

  const predictions = await new Promise((resolve) => {
    autocompleteService.getPlacePredictions(
      {
        input: place.name,
        bounds: atlantaBounds,
        componentRestrictions: { country: 'us' }
      },
      (suggestions, status) => {
        if (
          status === window.google.maps.places.PlacesServiceStatus.OK &&
          suggestions &&
          suggestions.length > 0
        ) {
          resolve(suggestions);
        } else {
          resolve([]);
        }
      }
    );
  });

  if (!predictions.length) {
    return place;
  }

  const topPrediction = predictions[0];
  const placesService = new window.google.maps.places.PlacesService(
    document.createElement('div')
  );

  const details = await new Promise((resolve) => {
    placesService.getDetails(
      {
        placeId: topPrediction.place_id,
        fields: ['geometry', 'name', 'formatted_address', 'types']
      },
      (result, status) => {
        if (
          status === window.google.maps.places.PlacesServiceStatus.OK &&
          result &&
          result.geometry &&
          result.geometry.location
        ) {
          resolve(result);
        } else {
          resolve(null);
        }
      }
    );
  });

  if (!details) {
    return place;
  }

  return {
    name: details.name || place.name,
    address: details.formatted_address,
    coordinates: `${details.geometry.location.lat()},${details.geometry.location.lng()}`,
    placeId: topPrediction.place_id,
    types: details.types,
    fromAutocomplete: true
  };
};

function App() {
  const [currentView, setCurrentView] = useState('search'); // 'search' or 'map'
  const [beginPlace, setBeginPlace] = useState({ name: '', coordinates: '', fromAutocomplete: false });
  const [destPlace, setDestPlace] = useState({ name: '', coordinates: '', fromAutocomplete: false });
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!beginPlace.name || !destPlace.name) {
      setError('Please select both starting and destination locations');
      return;
    }

    setLoading(true);
    setError('');
    setRoutes([]);

    try {
      // Only resolve if not already selected from dropdown
      const resolvedBegin = beginPlace.fromAutocomplete === true && beginPlace.coordinates
        ? beginPlace
        : await resolvePlaceCoordinates(beginPlace);
      
      const resolvedDest = destPlace.fromAutocomplete === true && destPlace.coordinates
        ? destPlace
        : await resolvePlaceCoordinates(destPlace);

      if (!resolvedBegin?.coordinates || !resolvedDest?.coordinates) {
        setError('Please pick locations from the suggestions so we can use exact coordinates.');
        setLoading(false);
        return;
      }

      // Keep displayed text in sync with the resolved place names
      setBeginPlace(resolvedBegin);
      setDestPlace(resolvedDest);

      const requestData = {
        begin_location: resolvedBegin.name,
        dest_location: resolvedDest.name,
        begin_coordinates: resolvedBegin.coordinates,
        dest_coordinates: resolvedDest.coordinates
      };

      // Determine API URL based on environment
      const apiUrl = (() => {
        const hostname = window.location.hostname;
        // Local development - use proxy
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
          return '/api/RouteSearch/';  
        }
        // Production - use Railway backend
        return 'https://buzzbus-production.up.railway.app/api/RouteSearch/';
      })();
      
      const response = await axios.post(apiUrl, requestData);

      if (response.data.routes) {
        setRoutes(response.data.routes);
      } else {
        setError(response.data.message || 'No routes found');
      }
    } catch (err) {
      setError('Failed to search routes. Please try again.');
      console.error('Error searching routes:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBeginPlaceSelect = useCallback((placeData) => {
    setBeginPlace({ ...placeData, fromAutocomplete: true });
  }, []);

  const handleDestPlaceSelect = useCallback((placeData) => {
    setDestPlace({ ...placeData, fromAutocomplete: true });
  }, []);

  const handleBeginPlaceChange = useCallback((e) => {
    setBeginPlace({ name: e.target.value, coordinates: '', fromAutocomplete: false });
  }, []);

  const handleDestPlaceChange = useCallback((e) => {
    setDestPlace({ name: e.target.value, coordinates: '', fromAutocomplete: false });
  }, []);

  return (
    <div className="App">
      {/* Header with GT stripe */}
      <div className="header-container">
        <div className="header-content">
          <div className="header-branding">
            <h1 className="header-title">BUZZ</h1>
            <span className="header-subtitle">GT TRANSIT</span>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="nav-container">
        <div className="nav-content">
          <button
            onClick={() => setCurrentView('search')}
            className={`nav-tab ${currentView === 'search' ? 'active' : ''}`}
          >
            ROUTE FINDER
          </button>
          <button
            onClick={() => setCurrentView('map')}
            className={`nav-tab ${currentView === 'map' ? 'active' : ''}`}
          >
            LIVE MAP
          </button>
        </div>
      </div>

      {currentView === 'map' ? (
        <Map />
      ) : (
        <main className="App-main">
        <form onSubmit={handleSearch} className="search-form">
          <div className="form-inputs">
            <div className="input-wrapper from-input">
              <div className="input-accent"></div>
              <PlaceAutocomplete
                id="begin-place"
                placeholder="FROM"
                value={beginPlace.name}
                onChange={handleBeginPlaceChange}
                onPlaceSelect={handleBeginPlaceSelect}
                className="route-input"
              />
            </div>

            <div className="input-wrapper to-input">
              <div className="input-accent dark"></div>
              <PlaceAutocomplete
                id="dest-place"
                placeholder="TO"
                value={destPlace.name}
                onChange={handleDestPlaceChange}
                onPlaceSelect={handleDestPlaceSelect}
                className="route-input"
              />
            </div>

            <button type="submit" disabled={loading} className="find-route-button">
              {loading ? 'SEARCHING...' : 'FIND ROUTE →'}
            </button>
          </div>
        </form>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {routes.length > 0 && (
          <div className="results-section">
            <div className="results-header">AVAILABLE ROUTES</div>
            
            <div className="routes-container">
              {routes.map((route, index) => {
                // Get next arrival time - prefer seconds, fallback to minutes
                const firstArrival = route.beginStop?.arrivalTimes && route.beginStop.arrivalTimes.length > 0
                  ? route.beginStop.arrivalTimes[0]
                  : null;
                
                let nextArrivalMinutes = null;
                let isArriving = false;
                let onTimeStatus = null;
                let arrivalTimeStr = null;
                
                if (firstArrival) {
                  // Calculate minutes from seconds if available (more accurate)
                  if (firstArrival.seconds !== null && firstArrival.seconds !== undefined) {
                    nextArrivalMinutes = Math.max(0, Math.floor(firstArrival.seconds / 60));
                  } else if (firstArrival.minutes !== null && firstArrival.minutes !== undefined) {
                    nextArrivalMinutes = firstArrival.minutes;
                  }
                  
                  isArriving = firstArrival.isArriving || false;
                  onTimeStatus = firstArrival.onTimeStatus;
                  arrivalTimeStr = firstArrival.time || firstArrival.estimateTime || firstArrival.scheduledTime;
                }
                
                const nextArrivalText = nextArrivalMinutes !== null && nextArrivalMinutes !== undefined
                  ? `${nextArrivalMinutes}`
                  : 'N/A';
                
                // Get status text
                let statusText = '';
                if (isArriving) {
                  statusText = 'Arriving';
                } else if (onTimeStatus === 0) {
                  statusText = 'On time';
                } else if (onTimeStatus === 2) {
                  statusText = 'Early';
                } else if (onTimeStatus === 3) {
                  statusText = 'Late';
                }
                
                // Count stops (approximate)
                const stopCount = route.beginStop && route.destStop ? 2 : 0;
                
                // Determine route color based on route name
                const routeNameUpper = (route.routeName || '').toUpperCase();
                let routeIconBg = '#3b82f6';
                if (routeNameUpper.includes('RED')) {
                  routeIconBg = '#dc2626';
                } else if (routeNameUpper.includes('BLUE')) {
                  routeIconBg = '#2563eb';
                } else if (routeNameUpper.includes('TROLLEY') || routeNameUpper.includes('YELLOW')) {
                  routeIconBg = '#eab308';
                }
                
                // First card is dark, others are white
                const isFirstCard = index === 0;
                
                return (
                  <div 
                    key={route.routeId} 
                    className={`route-card ${ 'route-card-light'}`}
                  >
                    <div className="route-card-content">
                      <div className="route-card-left">
                        <div className={`route-name ${ 'route-name-light'}`}>
                          {route.routeName || `Route ${route.routeId}`}
                        </div>
                        <div className={`route-time ${ 'route-time-light'}`}>
                          {nextArrivalText}
                          <span className="route-time-unit">min</span>
                        </div>
                        {statusText && (
                          <div className={`route-status ${'route-status-light'}`}>
                            {statusText}
                          </div>
                        )}
                      </div>
                      <div 
                        className="route-icon" 
                        style={{ 
                          backgroundColor: routeIconBg,
                          borderColor: isFirstCard ? '#ffffff' : '#1e293b'
                        }}
                      >
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M4 6C4 4.89543 4.89543 4 6 4H18C19.1046 4 20 4.89543 20 6V18C20 19.1046 19.1046 20 18 20H6C4.89543 20 4 19.1046 4 18V6Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                          <path d="M8 8H16M8 12H16M8 16H12" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      </div>
                    </div>
                    <div className={`route-footer ${isFirstCard ? 'route-footer-dark' : 'route-footer-light'}`}>
                      Next arrival: <span className="route-footer-bold">
                        {nextArrivalMinutes !== null ? `${nextArrivalMinutes} min` : 'N/A'}
                        {arrivalTimeStr && ` (${arrivalTimeStr})`}
                      </span>
                      {statusText && ` · ${statusText}`}
                      {route.beginStop?.name && ` · ${route.beginStop.name}`}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
        </main>
      )}
    </div>
  );
}

export default App;
