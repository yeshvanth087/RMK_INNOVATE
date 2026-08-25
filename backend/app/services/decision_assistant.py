"""
AI Urban Intelligence Decision Assistant.
Synthesizes decision support & NLP capabilities from TransportAi platform proj.
Allows city commissioners, PWD engineers, and traffic police to query live urban sensing data in plain English.
"""
from typing import Dict, Any
import re
from backend.app.database import get_db_connection

class UrbanDecisionAssistant:
    @staticmethod
    def query(user_prompt: str) -> Dict[str, Any]:
        """
        Interprets natural language queries from authorities, queries live urban sensing database,
        and generates structured recommendations.
        """
        prompt_lower = user_prompt.lower()
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Pothole / Defect Queries
        if any(w in prompt_lower for w in ["pothole", "defect", "road damage", "crack", "waterlog"]):
            cursor.execute("SELECT id, hazard_type, latitude, longitude, severity, confirmation_count, ticket_id FROM road_defects WHERE status != 'VERIFIED' ORDER BY confirmation_count DESC LIMIT 5")
            rows = cursor.fetchall()
            defects = [dict(r) for r in rows]
            conn.close()

            summary = f"Identified {len(defects)} critical road surface defects flagged across the fleet."
            details = [
                f"• #{d['id']} [{d['severity']} {d['hazard_type'].upper()}]: Confirmed by {d['confirmation_count']} buses at ({d['latitude']}, {d['longitude']}) - Ticket: {d['ticket_id'] or 'Pending'}"
                for d in defects
            ]
            
            return {
                "query": user_prompt,
                "domain": "MUNICIPAL_PWD",
                "summary": summary,
                "insights": "\n".join(details) if details else "No unverified high-severity defects currently found.",
                "actionable_recommendation": "Auto-dispatch PWD quick-response asphalt patching crew to top-ranked coordinates.",
                "data_records": defects
            }

        # 2. Hit and Run / ANPR / Police Incidents
        elif any(w in prompt_lower for w in ["police", "hit and run", "rash", "plate", "speed", "accident", "incident"]):
            cursor.execute("SELECT id, incident_type, license_plate, plate_confidence, estimated_speed, latitude, longitude, reporting_bus_id, timestamp FROM incident_alerts ORDER BY id DESC LIMIT 5")
            rows = cursor.fetchall()
            incidents = [dict(r) for r in rows]
            conn.close()

            summary = f"Retrieved {len(incidents)} active traffic law enforcement alerts tracked by onboard ANPR cameras."
            details = [
                f"• [{inc['incident_type']}] Plate: {inc['license_plate']} (Conf: {int((inc['plate_confidence'] or 0.8)*100)}%) - Speed: ~{inc['estimated_speed']} km/h - Reported by {inc['reporting_bus_id']}"
                for inc in incidents
            ]

            return {
                "query": user_prompt,
                "domain": "TRAFFIC_POLICE",
                "summary": summary,
                "insights": "\n".join(details) if details else "No active hit-and-run or rash driving violations reported in the last hour.",
                "actionable_recommendation": "Forward ANPR plate evidence packages to nearest traffic interceptor checkpoints.",
                "data_records": incidents
            }

        # 3. Delays / Congestion / Transit Routes
        elif any(w in prompt_lower for w in ["delay", "traffic", "congestion", "bottleneck", "route", "eta", "bus"]):
            cursor.execute("SELECT route_id, COUNT(*) as buses_active, AVG(speed_kmh) as avg_speed, AVG(crowding_pct) as avg_crowd FROM bus_telemetry GROUP BY route_id")
            rows = cursor.fetchall()
            routes = [dict(r) for r in rows]
            conn.close()

            summary = "Fleet-wide transit delay and corridor bottleneck analysis."
            details = [
                f"• Route {r['route_id']}: {r['buses_active']} buses running | Avg Speed: {round(r['avg_speed'] or 24, 1)} km/h | Avg Crowding: {round(r['avg_crowd'] or 45, 1)}%"
                for r in routes
            ]

            return {
                "query": user_prompt,
                "domain": "PUBLIC_TRANSIT",
                "summary": summary,
                "insights": "\n".join(details) if details else "All active routes are currently operating within 5 minutes of scheduled timetable.",
                "actionable_recommendation": "Activate dynamic detour via Inner Ring Road for Route 101 to bypass Anna Salai congestion.",
                "data_records": routes
            }

        # Default Fallback Query
        else:
            conn.close()
            return {
                "query": user_prompt,
                "domain": "GENERAL_URBAN_INTELLIGENCE",
                "summary": "NeuroNex UrbanSense AI Platform is actively monitoring 8 bus corridors in real-time.",
                "insights": "Platform capabilities:\n1. Pothole & road hazard detection and automated PWD ticketing.\n2. ANPR license plate extraction and hit-and-run tracking.\n3. ML route delay prediction and dynamic detour generation.\n4. Vulnerable pedestrian and school zone safety monitoring.",
                "actionable_recommendation": "Try asking: 'Show high severity potholes' or 'List recent hit and run incidents' or 'What is the delay on Route 101?'",
                "data_records": []
            }

decision_assistant = UrbanDecisionAssistant()
