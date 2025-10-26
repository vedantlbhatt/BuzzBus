import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [buildings, setBuildings] = useState([]);
  const [beginBuilding, setBeginBuilding] = useState('');
  const [destBuilding, setDestBuilding] = useState('');
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // Fetch available buildings
    axios.get('/api/buildings')
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
    if (!beginBuilding || !destBuilding) {
      setError('Please select both starting and destination buildings');
      return;
    }

    setLoading(true);
    setError('');
    setRoutes([]);

    try {
      const response = await axios.post('/api/RouteSearch', {
        begin_building: beginBuilding,
        dest_building: destBuilding
      });

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

  return (
    <div className="App">
      <header className="App-header">
        <h1>🚌 Georgia Tech Bus Route Finder</h1>
        <p>Discover the best bus routes between Georgia Tech buildings</p>
      </header>

      <main className="App-main">
        <form onSubmit={handleSearch} className="search-form">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="begin-building">Starting Building</label>
              <select
                id="begin-building"
                value={beginBuilding}
                onChange={(e) => setBeginBuilding(e.target.value)}
                required
              >
                <option value="">Select starting building</option>
                {buildings.map(building => (
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
                {buildings.map(building => (
                  <option key={building} value={building}>
                    {building}
                  </option>
                ))}
              </select>
            </div>
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
    </div>
  );
}

export default App;

