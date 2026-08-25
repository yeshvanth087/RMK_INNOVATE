"""
Telemetry Packager for Edge AI System.
Compiles detections, GPS coordinates, IMU telemetry, and incident alerts into lightweight JSON messages.
"""
from typing import Dict, Any, List, Optional
import time
import json

class TelemetryPackager:
    @staticmethod
    def create_payload(
        bus_id: str,
        route_id: str,
        latitude: float,
        longitude: float,
        speed_kmh: float,
        heading_deg: float,
        hazards: List[Dict[str, Any]],
        traffic: Dict[str, Any],
        vru_alerts: List[Dict[str, Any]],
        incident: Optional[Dict[str, Any]] = None,
        passenger_crowding_pct: float = 45.0
    ) -> Dict[str, Any]:
        """
        Creates an edge-optimized telemetry payload.
        Transmits structured metadata rather than heavy raw video.
        """
        payload = {
            "bus_id": bus_id,
            "route_id": route_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "epoch_timestamp": time.time(),
            "telemetry": {
                "latitude": round(latitude, 6),
                "longitude": round(longitude, 6),
                "speed_kmh": round(speed_kmh, 1),
                "heading_deg": round(heading_deg, 1),
                "crowding_pct": round(passenger_crowding_pct, 1)
            },
            "road_hazards": hazards,
            "traffic_density": traffic,
            "vru_safety_alerts": vru_alerts,
            "incident": incident
        }
        return payload

    @staticmethod
    def get_payload_size_bytes(payload: Dict[str, Any]) -> int:
        """Calculates payload byte size to monitor edge bandwidth consumption."""
        return len(json.dumps(payload).encode('utf-8'))
