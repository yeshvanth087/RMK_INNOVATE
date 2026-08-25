"""
Municipal PWD Work Orders & Maintenance Ticket Router.
Manages repair lifecycle: Auto-Generation -> Contractor Assignment -> AI Verification by sensing buses.
"""
from fastapi import APIRouter, HTTPException
from backend.app.database import get_db_connection
from backend.app.schemas import TicketStatusUpdate
from typing import List, Dict, Any

router = APIRouter(prefix="/api/tickets", tags=["PWD Maintenance"])

@router.get("/")
async def get_all_tickets() -> List[Dict[str, Any]]:
    """Returns all PWD repair work orders."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ticket_id, defect_id, defect_type, location_desc, latitude, longitude,
               severity, priority, assigned_department, status, created_at, updated_at
        FROM maintenance_tickets
        ORDER BY CASE priority 
            WHEN 'CRITICAL' THEN 1 
            WHEN 'HIGH' THEN 2 
            ELSE 3 
        END, created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.patch("/{ticket_id}/status")
async def update_ticket_status(ticket_id: str, status_data: TicketStatusUpdate):
    """Updates work order status (e.g., IN_PROGRESS, RESOLVED)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE maintenance_tickets
        SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE ticket_id = ?
    """, (status_data.status, ticket_id))
    
    # If resolved, update associated defect status
    if status_data.status == "RESOLVED":
        cursor.execute("UPDATE road_defects SET status = 'REPAIRED' WHERE ticket_id = ?", (ticket_id,))
    
    conn.commit()
    conn.close()
    return {"status": "UPDATED", "ticket_id": ticket_id, "new_status": status_data.status}

@router.post("/{ticket_id}/verify-repair")
async def simulate_ai_repair_verification(ticket_id: str):
    """
    Simulates subsequent sensing bus pass-through verifying that the pothole/defect is resolved.
    Upgrades ticket to AI_VERIFIED and closes road defect record.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE maintenance_tickets SET status = 'AI_VERIFIED', updated_at = CURRENT_TIMESTAMP WHERE ticket_id = ?", (ticket_id,))
    cursor.execute("UPDATE road_defects SET status = 'VERIFIED' WHERE ticket_id = ?", (ticket_id,))
    conn.commit()
    conn.close()
    return {"status": "AI_AUDIT_PASSED", "ticket_id": ticket_id, "verification_message": "Sensing bus fleet confirmed road surface restored to safe condition."}
