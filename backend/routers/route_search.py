from fastapi import APIRouter, HTTPException, Depends
from models import RouteSearchRequest, RouteSearchResponse, MapRoute, MapVehicle
from services.route_service import RouteService
from services.transloc_api_service import TranslocApiService

router = APIRouter(prefix="/api/RouteSearch", tags=["Route Search"])


def get_route_service() -> RouteService:
    """Dependency to get RouteService instance."""
    transloc_service = TranslocApiService()
    return RouteService(transloc_service)


@router.post("", response_model=RouteSearchResponse)
async def find_routes(
    request: RouteSearchRequest,
    route_service: RouteService = Depends(get_route_service)
):
    """Find bus routes between two points."""
    try:
        # Validate that we have at least one valid begin and destination point
        has_valid_begin = (
            request.begin_building or
            request.begin_coordinates or
            request.begin_location
        )
        has_valid_dest = (
            request.dest_building or
            request.dest_coordinates or
            request.dest_location
        )

        if not has_valid_begin or not has_valid_dest:
            raise HTTPException(
                status_code=400,
                detail="Both begin and destination points must be provided"
            )

        # Validate building names if provided
        if request.begin_building or request.dest_building:
            buildings = await route_service.get_buildings()
            building_names = {b.name for b in buildings}

            if request.begin_building and request.begin_building not in building_names:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid begin building name"
                )
            if request.dest_building and request.dest_building not in building_names:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid destination building name"
                )

        result = await route_service.find_routes(request)
        return result

    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@router.get("/map-routes")
async def get_map_routes(
    route_service: RouteService = Depends(get_route_service)
):
    """Get routes with map information."""
    try:
        routes = await route_service.get_map_routes()
        return routes
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@router.get("/map-vehicles")
async def get_map_vehicles(
    route_service: RouteService = Depends(get_route_service)
):
    """Get vehicles for map display."""
    try:
        vehicles = await route_service.get_map_vehicles()
        return vehicles
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

