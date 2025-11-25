import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import route_search, buildings, health
from config import settings
import uvicorn

app = FastAPI(
    title="BuzzBus API",
    description="API for finding bus routes at Georgia Tech",
    version="1.0.0"
)

# Configure CORS with origin validation for Vercel preview deployments
def is_allowed_origin(origin: str) -> bool:
    """Check if origin is allowed, including Vercel preview deployments."""
    allowed = settings.cors_origins.copy()
    
    # Allow localhost in any form
    if origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1"):
        return True
    
    # Check exact matches
    if origin in allowed:
        return True
    
    # Allow Vercel preview deployments (*.vercel.app)
    if origin.endswith(".vercel.app"):
        return True
    
    return False

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(route_search.router)
app.include_router(buildings.router)
app.include_router(health.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "BuzzBus API", "version": "1.0.0"}


if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", settings.port))
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=port,
        reload=False  # Disable reload in production
    )

