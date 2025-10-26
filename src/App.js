import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PlaceAutocomplete from './components/PlaceAutocomplete';
import Map from './components/Map';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('search'); // 'search' or 'map'
  const [buildings, setBuildings] = useState([]);
  const [beginBuilding, setBeginBuilding] = useState('');
  const [destBuilding, setDestBuilding] = useState('');
  const [beginPlace, setBeginPlace] = useState({ name: '', coordinates: '' });
  const [destPlace, setDestPlace] = useState({ name: '', coordinates: '' });
  const [searchMode, setSearchMode] = useState('buildings'); // 'buildings' or 'places'
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // Fetch available buildings from the API
    const apiUrl = process.env.NODE_ENV === 'production' 
      ? 'https://buzzbus-production.up.railway.app/api/buildings'  // Railway API URL
      : '/api/buildings';  // Development proxy
    
    axios.get(apiUrl)
      .then(response => {
        setBuildings(response.data);
      })
      .catch(err => {
        setError('Failed to load buildings');
        console.error('Error fetching buildings:', err);
      });
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    
    // Validate based on search mode
    if (searchMode === 'buildings') {
      if (!beginBuilding || !destBuilding) {
        setError('Please select both starting and destination buildings');
        return;
      }
    } else {
      if (!beginPlace.name || !destPlace.name) {
        setError('Please select both starting and destination locations');
        return;
      }
    }

    setLoading(true);
    setError('');
    setRoutes([]);

    try {
      let requestData;
      
      if (searchMode === 'buildings') {
        requestData = {
          begin_building: beginBuilding,
          dest_building: destBuilding
        };
      } else {
        requestData = {
          begin_location: beginPlace.name,
          dest_location: destPlace.name,
          begin_coordinates: beginPlace.coordinates,
          dest_coordinates: destPlace.coordinates
        };
      }

      const apiUrl = process.env.NODE_ENV === 'production' 
        ? 'https://buzzbus-production.up.railway.app/api/RouteSearch'  // Railway API URL
        : '/api/RouteSearch';  // Development proxy
      
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

  const switchSearchMode = (mode) => {
    setSearchMode(mode);
    setBeginBuilding('');
    setDestBuilding('');
    setBeginPlace({ name: '', coordinates: '' });
    setDestPlace({ name: '', coordinates: '' });
    setRoutes([]);
    setError('');
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🚌 Georgia Tech Bus Route Finder</h1>
        <p>Discover the best bus routes between Georgia Tech buildings</p>
        
        <div className="navigation-tabs">
          <button 
            className={`nav-tab ${currentView === 'search' ? 'active' : ''}`}
            onClick={() => setCurrentView('search')}
          >
            🔍 Route Search
          </button>
          <button 
            className={`nav-tab ${currentView === 'map' ? 'active' : ''}`}
            onClick={() => setCurrentView('map')}
          >
            🗺️ Live Map
          </button>
        </div>
      </header>

      {currentView === 'map' ? (
        <Map />
      ) : (
        <main className="App-main">
        <form onSubmit={handleSearch} className="search-form">
          {/* Search Mode Toggle */}
          <div className="search-mode-toggle">
            <button
              type="button"
              className={`mode-button ${searchMode === 'buildings' ? 'active' : ''}`}
              onClick={() => switchSearchMode('buildings')}
            >
              🏢 Campus Buildings
            </button>
            <button
              type="button"
              className={`mode-button ${searchMode === 'places' ? 'active' : ''}`}
              onClick={() => switchSearchMode('places')}
            >
              📍 Any Location
            </button>
          </div>

          <div className="form-row">
            {searchMode === 'buildings' ? (
              <>
                <div className="form-group">
                  <label htmlFor="begin-building">Starting Building</label>
                  <select
                    id="begin-building"
                    value={beginBuilding}
                    onChange={(e) => setBeginBuilding(e.target.value)}
                    required
                  >
                    <option value="">Select starting building</option>
                    {buildings && buildings.length > 0 && buildings.map(building => (
                      <option key={building} value={building}>
                        {building}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="dest-building">Destination Building</label>
                  <select
                    id="dest-building"
                    value={destBuilding}
                    onChange={(e) => setDestBuilding(e.target.value)}
                    required
                  >
                    <option value="">Select destination building</option>
                    {buildings && buildings.length > 0 && buildings.map(building => (
                      <option key={building} value={building}>
                        {building}
                      </option>
                    ))}
                  </select>
                </div>
              </>
            ) : (
              <>
                <div className="form-group">
                  <label htmlFor="begin-place">Starting Location</label>
                  <PlaceAutocomplete
                    id="begin-place"
                    placeholder="Search for a location near Georgia Tech..."
                    value={beginPlace.name}
                    onChange={handleBeginPlaceChange}
                    onPlaceSelect={handleBeginPlaceSelect}
                    className="place-input"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="dest-place">Destination Location</label>
                  <PlaceAutocomplete
                    id="dest-place"
                    placeholder="Search for a location near Georgia Tech..."
                    value={destPlace.name}
                    onChange={handleDestPlaceChange}
                    onPlaceSelect={handleDestPlaceSelect}
                    className="place-input"
                  />
                </div>
              </>
            )}
          </div>

          <button type="submit" disabled={loading} className="search-button">
            {loading ? 'Searching...' : 'Find Best Bus Route'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {routes.length > 0 && (
          <div className="results-section">
            <h2>Best Bus Routes</h2>
            <p className="route-info">
              From <strong>{beginBuilding}</strong> to <strong>{destBuilding}</strong>
            </p>
            
            <div className="routes-container">
              {routes.map((route, index) => (
                <div key={route.routeId} className="route-card">
                  <div className="route-header">
                    <h3>🚍 {route.routeName}</h3>
                    <span className="route-id">Route: {route.routeId}</span>
                  </div>
                  
                  <div className="route-details">
                    <div className="stop-info">
                      <div className="stop-item">
                        <h4>Start Stop</h4>
                        <p className="stop-name">{route.beginStop.name}</p>
                        <p className="stop-distance">
                          {route.beginStop.distance}m from {beginBuilding}
                        </p>
                      </div>
                      
                      <div className="stop-item">
                        <h4>Destination Stop</h4>
                        <p className="stop-name">{route.destStop.name}</p>
                        <p className="stop-distance">
                          {route.destStop.distance}m from {destBuilding}
                        </p>
                      </div>
                    </div>
                    
                    <div className="total-distance">
                      <strong>Total Walking Distance: {route.totalWalkingDistance}m</strong>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        </main>
      )}
    </div>
  );
}

export default App;

