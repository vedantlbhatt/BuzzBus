import React, { useState } from 'react';
import axios from 'axios';
import PlaceAutocomplete from './components/PlaceAutocomplete';
import Map from './components/Map';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('search'); // 'search' or 'map'
  const [beginPlace, setBeginPlace] = useState({ name: '', coordinates: '' });
  const [destPlace, setDestPlace] = useState({ name: '', coordinates: '' });
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
      const requestData = {
        begin_location: beginPlace.name,
        dest_location: destPlace.name,
        begin_coordinates: beginPlace.coordinates,
        dest_coordinates: destPlace.coordinates
      };

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

  const handleBeginPlaceSelect = (placeData) => {
    setBeginPlace(placeData);
  };

  const handleDestPlaceSelect = (placeData) => {
    setDestPlace(placeData);
  };

  const handleBeginPlaceChange = (e) => {
    setBeginPlace({ name: e.target.value, coordinates: '' });
  };

  const handleDestPlaceChange = (e) => {
    setDestPlace({ name: e.target.value, coordinates: '' });
  };

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
                    className={`route-card ${isFirstCard ? 'route-card-dark' : 'route-card-light'}`}
                  >
                    <div className="route-card-content">
                      <div className="route-card-left">
                        <div className={`route-name ${isFirstCard ? 'route-name-dark' : 'route-name-light'}`}>
                          {route.routeName || `Route ${route.routeId}`}
                        </div>
                        <div className={`route-time ${isFirstCard ? 'route-time-dark' : 'route-time-light'}`}>
                          {nextArrivalText}
                          <span className="route-time-unit">min</span>
                        </div>
                        {statusText && (
                          <div className={`route-status ${isFirstCard ? 'route-status-dark' : 'route-status-light'}`}>
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

