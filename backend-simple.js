const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors({
  origin: [
    'http://localhost:3000',
    'https://buzz-bus.vercel.app',
    'https://*.vercel.app',
    'https://*.netlify.app'
  ],
  credentials: true
}));
app.use(express.json());

// Hardcoded buildings for immediate functionality
const buildings = [
  "Tech Tower",
  "Georgia Tech Library", 
  "Clough Commons",
  "Hopkins Hall",
  "Glenn Hall",
  "North Ave East",
  "Student Center",
  "Campus Rec Center",
  "D.M. Smith",
  "Bobby Dodd Stadium"
];

// Buildings endpoint
app.get('/api/buildings', (req, res) => {
  res.json(buildings);
});

// Route search endpoint (simplified)
app.post('/api/RouteSearch', (req, res) => {
  const { begin_building, dest_building } = req.body;
  
  // Mock route response
  const mockRoute = {
    routes: [{
      routeId: "GT-001",
      routeName: "Campus Connector",
      beginStop: {
        name: `${begin_building} Stop`,
        distance: 50
      },
      destStop: {
        name: `${dest_building} Stop`, 
        distance: 75
      },
      totalWalkingDistance: 125
    }]
  };
  
  res.json(mockRoute);
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
