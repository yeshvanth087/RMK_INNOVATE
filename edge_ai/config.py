"""
Edge AI Configuration for Onboard Bus Perception Unit.
Handles camera stream endpoints, model thresholds, and telemetry frequencies.
"""
from dataclasses import dataclass

@dataclass
class EdgeConfig:
    BUS_ID: str = "BUS-BEL-104"
    ROUTE_ID: str = "RT-45A"
    BACKEND_URL: str = "http://127.0.0.1:8000/api/telemetry/ping"
    INCIDENT_URL: str = "http://127.0.0.1:8000/api/incidents/report"
    
    # Processing Rates
    INFERENCE_FPS: int = 5
    TELEMETRY_INTERVAL_SEC: float = 3.0
    
    # Confidence Thresholds
    POTHOLE_CONFIDENCE_THRESHOLD: float = 0.65
    WATERLOGGING_CONFIDENCE_THRESHOLD: float = 0.70
    ANPR_CONFIDENCE_THRESHOLD: float = 0.75
    PEDESTRIAN_RISK_THRESHOLD: float = 0.60
    
    # Edge Buffer Settings
    SNAPSHOT_ON_INCIDENT: bool = True
    MAX_BUFFER_FRAMES: int = 150  # 5 seconds at 30 fps
