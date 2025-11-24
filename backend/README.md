# BuzzBus FastAPI Backend

This is the FastAPI backend for the BuzzBus application, converted from .NET.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file (or use the default settings):
```bash
cp .env.example .env
```

3. Run the server from the backend directory:
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

Or use the run script:
```bash
cd backend
chmod +x run.sh
./run.sh
```

## API Endpoints

- `GET /api/Health` - Health check
- `GET /api/Buildings` - Get list of buildings
- `POST /api/RouteSearch` - Find routes between two points
- `GET /api/RouteSearch/map-routes` - Get routes for map display
- `GET /api/RouteSearch/map-vehicles` - Get vehicles for map display

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration settings
├── models.py              # Pydantic models
├── requirements.txt       # Python dependencies
├── routers/              # API route handlers
│   ├── route_search.py
│   ├── buildings.py
│   └── health.py
└── services/             # Business logic
    ├── transloc_api_service.py
    └── route_service.py
```

## Environment Variables

- `TRANSLOC_API_KEY` - API key for Transloc API
- `TRANSLOC_BASE_URL` - Base URL for Transloc API
- `PORT` - Server port (default: 5000)
- `HOST` - Server host (default: 0.0.0.0)

