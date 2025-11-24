from fastapi import APIRouter, HTTPException, Depends
from typing import List
from services.route_service import RouteService
from services.transloc_api_service import TranslocApiService

router = APIRouter(prefix="/api/buildings", tags=["Buildings"])


def get_route_service() -> RouteService:
    """Dependency to get RouteService instance."""
    transloc_service = TranslocApiService()
    return RouteService(transloc_service)


@router.get("", response_model=List[str])
async def get_buildings(
    route_service: RouteService = Depends(get_route_service)
):
    """Get list of available buildings."""
    try:
        buildings = await route_service.get_buildings()
        return [b.name for b in buildings]
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

