"""
Pydantic Schemas for Request and Response Validation.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class TelemetryCoords(BaseModel):
    latitude: float
    longitude: float
    speed_kmh: float
    heading_deg: float
    crowding_pct: Optional[float] = 30.0

class RoadHazardIn(BaseModel):
    type: str
    severity: str
    confidence: float
    relative_position: Optional[str] = "lane_center"
    bounding_box: Optional[List[int]] = None
    detected_at: Optional[float] = None

class VehicleDetails(BaseModel):
    type: str
    model: str
    color: str

class IncidentIn(BaseModel):
    incident_type: str
    severity: str
    license_plate: str
    plate_confidence: float
    vehicle_details: Optional[Dict[str, Any]] = None
    estimated_offender_speed_kmh: Optional[float] = None
    tracking_id: Optional[str] = None
    evidence_snapshot: Optional[str] = None

class TrafficDensityIn(BaseModel):
    vehicle_counts: Dict[str, int]
    total_vehicles: int
    total_pcu: float
    density_level: str
    is_bottleneck: bool

class VRUAlertIn(BaseModel):
    category: str
    risk_level: str
    pedestrian_count: int
    is_crossing: bool
    confidence: float

class TelemetryPingIn(BaseModel):
    bus_id: str
    route_id: str
    timestamp: str
    epoch_timestamp: Optional[float] = None
    telemetry: TelemetryCoords
    road_hazards: List[RoadHazardIn] = []
    traffic_density: Optional[TrafficDensityIn] = None
    vru_safety_alerts: List[VRUAlertIn] = []
    incident: Optional[IncidentIn] = None

class TicketStatusUpdate(BaseModel):
    status: str # 'OPEN', 'IN_PROGRESS', 'RESOLVED'

class RouteDelayQuery(BaseModel):
    route_id: str
    hour_of_day: int
    weather_condition: Optional[str] = "CLEAR" # CLEAR, RAIN, HEAVY_RAIN
    current_crowding_pct: Optional[float] = 50.0

class DynamicRouteQuery(BaseModel):
    origin: str
    destination: str
    avoid_hazards: bool = True
