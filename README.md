# BuzzBus - Georgia Tech Bus Route Finder

A modern web application that helps Georgia Tech students and visitors find the best bus routes between campus buildings and nearby locations.

## Architecture

- **Frontend**: React 18 with modern CSS
- **Backend**: FastAPI (Python)
- **External API**: TransLoc API for real-time bus data

## Prerequisites

- Node.js 16+ and npm
- Python 3.11+
- TransLoc API key and base URL

### Alternative: Docker Setup

If you prefer not to install Python locally, you can use Docker:

- Docker Desktop
- Docker Compose

## Docker Setup (Alternative)

1. Copy the environment file:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` with your TransLoc API credentials:
   ```
   TRANSLOC_API_KEY=your_api_key
   TRANSLOC_BASE_URL=https://gatech.transloc.com/Services/JSONPRelay.svc
   ```

3. Run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

This will start both the FastAPI backend and React frontend in containers.

## Setup Instructions

### 1. Backend (FastAPI)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables (optional, defaults are set):
   ```bash
   export TRANSLOC_API_KEY=your_api_key
   export TRANSLOC_BASE_URL=https://gatech.transloc.com/Services/JSONPRelay.svc
   ```

   Or create a `.env` file in the `backend/` directory.

4. Run the API:
   ```bash
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 5000
   ```

   Or use the run script:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

The API will be available at `http://localhost:5000`
API documentation: `http://localhost:5000/docs`

### 2. Frontend (React)

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

The React app will be available at `http://localhost:3000`

## Quick Start (Both Services)

Use the provided startup scripts:

**Linux/Mac:**
```bash
chmod +x start-dev.sh
./start-dev.sh
```

**Windows:**
```bash
start-dev.bat
```

## API Endpoints

- `GET /api/health` - Health check endpoint
- `GET /api/buildings` - Get list of available campus buildings
- `POST /api/RouteSearch` - Find bus routes between two locations
- `GET /api/RouteSearch/map-routes` - Get routes for map display
- `GET /api/RouteSearch/map-vehicles` - Get vehicle positions for map

## Features

- **Building-to-Building Search**: Select from predefined Georgia Tech buildings
- **Location-to-Location Search**: Use Google Places API for custom locations
- **Real-time Data**: Shows only routes with currently active buses
- **Walking Distance**: Calculates total walking distance to/from bus stops
- **Bus Arrival Times**: Shows ETA for next buses at stops
- **Interactive Map**: Visual display of routes and vehicle positions
- **Responsive Design**: Works on desktop and mobile devices

## Project Structure

```
BuzzBus/
├── backend/                      # FastAPI backend
│   ├── main.py                  # Application entry point
│   ├── config.py                # Configuration settings
│   ├── models.py                # Pydantic models
│   ├── routers/                 # API route handlers
│   │   ├── route_search.py
│   │   ├── buildings.py
│   │   └── health.py
│   ├── services/                # Business logic services
│   │   ├── route_service.py
│   │   └── transloc_api_service.py
│   ├── Dockerfile               # Docker configuration
│   └── requirements.txt         # Python dependencies
├── src/                         # React frontend
│   ├── App.js                   # Main React component
│   ├── App.css                  # Styling
│   ├── components/              # React components
│   │   ├── Map.js
│   │   └── PlaceAutocomplete.js
│   └── index.js                 # React entry point
├── public/                      # Static assets
└── package.json                 # Node.js dependencies
```

## Development

### Running Both Services

**Option 1: Use startup scripts (recommended)**
```bash
./start-dev.sh  # Linux/Mac
# or
start-dev.bat   # Windows
```

**Option 2: Manual start**

1. Start the FastAPI backend (Terminal 1):
   ```bash
   cd backend
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 5000
   ```

2. Start the React app (Terminal 2):
   ```bash
   npm start
   ```

### Building for Production

1. Build the React app:
   ```bash
   npm run build
   ```

2. The FastAPI backend is ready to deploy (see `backend/RAILWAY_DEPLOYMENT.md` for Railway deployment)

## Configuration

The application requires the following environment variables:

- `TRANSLOC_API_KEY` - Your TransLoc API key (default: provided)
- `TRANSLOC_BASE_URL` - Georgia Tech TransLoc API base URL (default: provided)

These can be set in:
- Environment variables
- `.env` file in the `backend/` directory
- Railway/Render environment variables (for production)

## Deployment

### Railway Deployment

1. Go to Railway dashboard
2. Select your service
3. Settings → Root Directory
4. Change to: `backend`
5. Railway will auto-detect Python and deploy FastAPI

See `backend/RAILWAY_DEPLOYMENT.md` for detailed instructions.

## Testing

Test the FastAPI backend:
```bash
cd backend
python test_api.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
