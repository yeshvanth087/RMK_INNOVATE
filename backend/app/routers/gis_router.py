"""
GIS & Map Layer Router.
Serves structured GeoJSON and coordinate streams for Leaflet / Mapbox GIS visualizations.
"""
from fastapi import APIRouter
from backend.app.database import get_db_connection
from typing import Dict, Any, List

router = APIRouter(prefix="/api/gis", tags=["GIS & Maps"])

@router.get("/fleet-live")
async def get_live_fleet() -> List[Dict[str, Any]]:
    """Returns real-time GPS locations and statuses for all active sensing buses."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT bus_id, route_id, latitude, longitude, speed_kmh, heading_deg, crowding_pct, last_updated
        FROM bus_telemetry
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.get("/road-defects-geojson")
async def get_road_defects_geojson() -> Dict[str, Any]:
    """Returns all active road defects formatted as GeoJSON FeatureCollection."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, hazard_type, latitude, longitude, severity, confidence, relative_position, confirmation_count, status, ticket_id, first_detected
        FROM road_defects
        WHERE status != 'VERIFIED'
    """)
    rows = cursor.fetchall()
    conn.close()

    features = []
    for r in rows:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [r["longitude"], r["latitude"]]
            },
            "properties": {
                "id": r["id"],
                "hazard_type": r["hazard_type"],
                "severity": r["severity"],
                "confidence": r["confidence"],
                "relative_position": r["relative_position"],
                "confirmation_count": r["confirmation_count"],
                "status": r["status"],
                "ticket_id": r["ticket_id"],
                "first_detected": r["first_detected"]
            }
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }

@router.get("/traffic-corridors")
async def get_traffic_corridors() -> List[Dict[str, Any]]:
    """Returns active traffic density metrics per urban corridor."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT corridor_id, route_id, segment_name, latitude, longitude, total_pcu, density_level, avg_speed_kmh, is_bottleneck, last_updated
        FROM traffic_hotspots
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
