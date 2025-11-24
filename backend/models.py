from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class Building(BaseModel):
    name: str
    latitude: float
    longitude: float


class ArrivalTime(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    minutes: Optional[int] = None
    vehicle_id: Optional[str] = Field(None, alias="vehicleId")
    vehicle_name: Optional[str] = Field(None, alias="vehicleName")


class StopInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    name: str
    distance: float
    route_stop_id: Optional[str] = Field(None, alias="routeStopId")
    arrival_times: List[ArrivalTime] = Field(default_factory=list, alias="arrivalTimes")


class RouteResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    route_id: str = Field(alias="routeId")
    route_name: str = Field(alias="routeName")
    begin_stop: StopInfo = Field(alias="beginStop")
    dest_stop: StopInfo = Field(alias="destStop")
    total_walking_distance: float = Field(alias="totalWalkingDistance")


class RouteSearchRequest(BaseModel):
    begin_building: Optional[str] = Field(None, alias="begin_building")
    dest_building: Optional[str] = Field(None, alias="dest_building")
    begin_location: Optional[str] = Field(None, alias="begin_location")
    dest_location: Optional[str] = Field(None, alias="dest_location")
    begin_coordinates: Optional[str] = Field(None, alias="begin_coordinates")
    dest_coordinates: Optional[str] = Field(None, alias="dest_coordinates")


class RouteSearchResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    routes: List[RouteResult] = Field(default_factory=list)
    begin_building: str = Field(default="", alias="beginBuilding")
    dest_building: str = Field(default="", alias="destBuilding")
    begin_location: str = Field(default="", alias="beginLocation")
    dest_location: str = Field(default="", alias="destLocation")


class MapStop(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    route_stop_id: str = Field(default="", alias="routeStopId")
    route_id: str = Field(default="", alias="routeId")
    description: str = Field(default="")
    latitude: float = 0.0
    longitude: float = 0.0
    order: int = 0
    show_estimates_on_map: bool = Field(default=False, alias="showEstimatesOnMap")
    show_defaulted_on_map: bool = Field(default=False, alias="showDefaultedOnMap")


class MapRoute(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    route_id: str = Field(default="", alias="routeId")
    description: str = Field(default="")
    map_line_color: str = Field(default="#000000", alias="mapLineColor")
    map_latitude: float = Field(default=0.0, alias="mapLatitude")
    map_longitude: float = Field(default=0.0, alias="mapLongitude")
    map_zoom: int = Field(default=0, alias="mapZoom")
    is_visible_on_map: bool = Field(default=False, alias="isVisibleOnMap")
    is_checked_on_map: bool = Field(default=False, alias="isCheckedOnMap")
    hide_route_line: bool = Field(default=False, alias="hideRouteLine")
    encoded_polyline: str = Field(default="", alias="encodedPolyline")
    stops: List[MapStop] = Field(default_factory=list)


class MapVehicle(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    vehicle_id: str = Field(default="", alias="vehicleId")
    route_id: str = Field(default="", alias="routeId")
    name: str = Field(default="")
    latitude: float = 0.0
    longitude: float = 0.0
    ground_speed: float = Field(default=0.0, alias="groundSpeed")
    heading: float = 0.0
    seconds: int = 0
    is_on_route: bool = Field(default=False, alias="isOnRoute")
    is_delayed: bool = Field(default=False, alias="isDelayed")

