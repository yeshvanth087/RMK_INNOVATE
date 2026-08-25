"""
Police Incidents & ANPR Alert Router.
Supports Traffic Police Law Enforcement monitoring, hit-and-run tracing, and evidence export.
"""
from fastapi import APIRouter, HTTPException, Query
from backend.app.database import get_db_connection
from typing import List, Dict, Any, Optional

router = APIRouter(prefix="/api/incidents", tags=["Police Incidents & ANPR"])

@router.get("/active")
async def get_active_incidents(limit: int = 50) -> List[Dict[str, Any]]:
    """Returns real-time police incidents and ANPR alert stream."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, incident_type, severity, license_plate, plate_confidence,
               vehicle_details, estimated_speed, latitude, longitude,
               reporting_bus_id, tracking_id, evidence_snapshot, status, timestamp
        FROM incident_alerts
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.get("/search")
async def search_by_plate(plate: str = Query(..., description="Partial or full license plate string")) -> List[Dict[str, Any]]:
    """Searches for vehicles by license plate number across the sensing fleet history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    search_query = f"%{plate.strip()}%"
    cursor.execute("""
        SELECT id, incident_type, severity, license_plate, plate_confidence,
               vehicle_details, estimated_speed, latitude, longitude,
               reporting_bus_id, tracking_id, evidence_snapshot, status, timestamp
        FROM incident_alerts
        WHERE license_plate LIKE ?
        ORDER BY id DESC
    """, (search_query,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.post("/{incident_id}/dispatch")
async def dispatch_interceptor(incident_id: int):
    """Flags incident as DISPATCHED to local traffic police patrol unit."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE incident_alerts SET status = 'DISPATCHED' WHERE id = ?", (incident_id,))
    conn.commit()
    conn.close()
    return {"status": "DISPATCH_CONFIRMED", "incident_id": incident_id}
