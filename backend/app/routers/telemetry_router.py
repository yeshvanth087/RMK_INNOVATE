"""
Telemetry Ingestion Router.
Receives structured edge JSON telemetry pings from sensing buses.
"""
from fastapi import APIRouter, HTTPException
from backend.app.schemas import TelemetryPingIn
from backend.app.database import get_db_connection
from backend.app.services.spatial_clustering import SpatialClusteringService
import json

router = APIRouter(prefix="/api/telemetry", tags=["Telemetry"])

@router.post("/ping")
async def receive_telemetry_ping(ping: TelemetryPingIn):
    """
    Ingests live bus telemetry packet.
    Deduplicates hazards, updates bus live location, records traffic and incident data.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Update Bus Live Telemetry
    cursor.execute("""
        INSERT INTO bus_telemetry (bus_id, route_id, latitude, longitude, speed_kmh, heading_deg, crowding_pct, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(bus_id) DO UPDATE SET
            route_id = excluded.route_id,
            latitude = excluded.latitude,
            longitude = excluded.longitude,
            speed_kmh = excluded.speed_kmh,
            heading_deg = excluded.heading_deg,
            crowding_pct = excluded.crowding_pct,
            last_updated = CURRENT_TIMESTAMP
    """, (
        ping.bus_id,
        ping.route_id,
        ping.telemetry.latitude,
        ping.telemetry.longitude,
        ping.telemetry.speed_kmh,
        ping.telemetry.heading_deg,
        ping.telemetry.crowding_pct or 40.0
    ))

    # 2. Update Traffic Hotspot if density data present
    if ping.traffic_density:
        corridor_id = f"CORR-{ping.route_id}"
        cursor.execute("""
            INSERT INTO traffic_hotspots (corridor_id, route_id, segment_name, latitude, longitude, total_pcu, density_level, avg_speed_kmh, is_bottleneck, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(corridor_id) DO UPDATE SET
                latitude = excluded.latitude,
                longitude = excluded.longitude,
                total_pcu = excluded.total_pcu,
                density_level = excluded.density_level,
                avg_speed_kmh = excluded.avg_speed_kmh,
                is_bottleneck = excluded.is_bottleneck,
                last_updated = CURRENT_TIMESTAMP
        """, (
            corridor_id,
            ping.route_id,
            f"Segment near ({ping.telemetry.latitude:.3f}, {ping.telemetry.longitude:.3f})",
            ping.telemetry.latitude,
            ping.telemetry.longitude,
            ping.traffic_density.total_pcu,
            ping.traffic_density.density_level,
            ping.telemetry.speed_kmh,
            1 if ping.traffic_density.is_bottleneck else 0
        ))

    # 3. Log Incident if triggered
    if ping.incident:
        cursor.execute("""
            INSERT INTO incident_alerts (
                incident_type, severity, license_plate, plate_confidence,
                vehicle_details, estimated_speed, latitude, longitude,
                reporting_bus_id, tracking_id, evidence_snapshot, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE')
        """, (
            ping.incident.incident_type,
            ping.incident.severity,
            ping.incident.license_plate,
            ping.incident.plate_confidence,
            json.dumps(ping.incident.vehicle_details or {}),
            ping.incident.estimated_offender_speed_kmh or 0.0,
            ping.telemetry.latitude,
            ping.telemetry.longitude,
            ping.bus_id,
            ping.incident.tracking_id or f"TRK-{ping.bus_id}",
            ping.incident.evidence_snapshot
        ))

    conn.commit()
    conn.close()

    # 4. Process Road Hazards through Spatial Deduplication Clustering
    clustering_results = []
    for hazard in ping.road_hazards:
        res = SpatialClusteringService.process_hazard_ping(
            hazard_type=hazard.type,
            lat=ping.telemetry.latitude,
            lng=ping.telemetry.longitude,
            severity=hazard.severity,
            confidence=hazard.confidence,
            relative_pos=hazard.relative_position or "lane_center"
        )
        clustering_results.append(res)

    return {
        "status": "INGESTED_SUCCESSFULLY",
        "bus_id": ping.bus_id,
        "hazards_processed": len(clustering_results),
        "incident_logged": ping.incident is not None
    }
