"""
Spatial Clustering & Defect Deduplication Engine.
Implements distance-based clustering (Haversine ST_ClusterDBSCAN equivalent) to merge
duplicate pothole/hazard detections from multiple sensing buses into a single verified master record.
"""
from typing import Dict, Any, Optional
import sqlite3
import time
from backend.app.database import get_db_connection, haversine_distance_meters

CLUSTERING_RADIUS_METERS = 15.0  # Merge duplicate pings within 15 meters

class SpatialClusteringService:
    @staticmethod
    def process_hazard_ping(
        hazard_type: str,
        lat: float,
        lng: float,
        severity: str,
        confidence: float,
        relative_pos: str = "lane_center"
    ) -> Dict[str, Any]:
        """
        Matches incoming hazard against existing active road defects.
        If match found within 15m radius:
            - Merges coordinates (weighted running average)
            - Increments confirmation_count
            - Updates confidence
            - Triggers PWD Ticket if threshold exceeded
        Else:
            - Creates new road defect record
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        # Find existing defects of the same type within candidate bounding box
        # Roughly 0.001 deg lat/lon ~ 111 meters
        cursor.execute("""
            SELECT id, hazard_type, latitude, longitude, severity, confidence, confirmation_count, status, ticket_id
            FROM road_defects
            WHERE hazard_type = ? 
              AND status != 'VERIFIED'
              AND latitude BETWEEN ? AND ?
              AND longitude BETWEEN ? AND ?
        """, (hazard_type, lat - 0.002, lat + 0.002, lng - 0.002, lng + 0.002))
        
        candidates = cursor.fetchall()
        matched_defect = None

        for row in candidates:
            dist = haversine_distance_meters(lat, lng, row["latitude"], row["longitude"])
            if dist <= CLUSTERING_RADIUS_METERS:
                matched_defect = row
                break

        if matched_defect:
            # Merge & update existing defect
            new_count = matched_defect["confirmation_count"] + 1
            # Weighted average coordinate
            updated_lat = round((matched_defect["latitude"] * matched_defect["confirmation_count"] + lat) / new_count, 6)
            updated_lng = round((matched_defect["longitude"] * matched_defect["confirmation_count"] + lng) / new_count, 6)
            updated_conf = max(matched_defect["confidence"], confidence)
            
            # Upgrade severity if high/critical reported
            severity_order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
            new_severity = matched_defect["severity"]
            if severity_order.get(severity, 1) > severity_order.get(matched_defect["severity"], 1):
                new_severity = severity

            cursor.execute("""
                UPDATE road_defects
                SET latitude = ?, longitude = ?, severity = ?, confidence = ?, 
                    confirmation_count = ?, last_confirmed = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (updated_lat, updated_lng, new_severity, updated_conf, new_count, matched_defect["id"]))

            defect_id = matched_defect["id"]
            ticket_id = matched_defect["ticket_id"]

            # Auto-generate PWD Maintenance Ticket if confirmed by 2+ buses or CRITICAL
            if not ticket_id and (new_count >= 2 or new_severity in ["HIGH", "CRITICAL"]):
                ticket_id = f"TKT-PWD-{int(time.time())}-{defect_id}"
                priority = "CRITICAL" if new_severity == "CRITICAL" else ("HIGH" if new_severity == "HIGH" else "NORMAL")
                
                cursor.execute("""
                    INSERT INTO maintenance_tickets (ticket_id, defect_id, defect_type, location_desc, latitude, longitude, severity, priority, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'OPEN')
                """, (ticket_id, defect_id, hazard_type, f"Auto-detected near ({updated_lat}, {updated_lng})", updated_lat, updated_lng, new_severity, priority))

                cursor.execute("UPDATE road_defects SET ticket_id = ?, status = 'WORK_ORDER_ISSUED' WHERE id = ?", (ticket_id, defect_id))

            conn.commit()
            conn.close()
            return {"action": "MERGED", "defect_id": defect_id, "confirmation_count": new_count, "ticket_id": ticket_id}

        else:
            # Create new defect
            cursor.execute("""
                INSERT INTO road_defects (hazard_type, latitude, longitude, severity, confidence, relative_position, confirmation_count, status)
                VALUES (?, ?, ?, ?, ?, ?, 1, 'REPORTED')
            """, (hazard_type, lat, lng, severity, confidence, relative_pos))
            
            new_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return {"action": "CREATED", "defect_id": new_id, "confirmation_count": 1, "ticket_id": None}
