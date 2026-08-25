"""
NeuroNex UrbanSense AI - Central Backend Platform
FastAPI Server for Edge Bus Telemetry Ingestion, Spatial Deduplication,
ML Analytics, and Authority Command Center Portals.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.app.database import init_db, get_db_connection
from backend.app.routers import (
    telemetry_router,
    gis_router,
    incidents_router,
    tickets_router,
    analytics_router,
    assistant_router
)

app = FastAPI(
    title="NeuroNex UrbanSense AI Platform",
    description="AI-Powered Mobile Urban Intelligence Platform Using Public Transport Fleet (BEL - SIH26124)",
    version="1.0.0"
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(telemetry_router.router)
app.include_router(gis_router.router)
app.include_router(incidents_router.router)
app.include_router(tickets_router.router)
app.include_router(analytics_router.router)
app.include_router(assistant_router.router)

# Static files directory for Frontend GIS Command Center
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    """Serves the Unified GIS Command Center UI."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "NeuroNex UrbanSense AI Backend Running. Visit /docs for Swagger API."}

@app.on_event("startup")
def startup_seed_data():
    """Initializes schema and seeds realistic baseline sensing data."""
    init_db()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if road_defects empty; if so, populate initial real-world baseline
    cursor.execute("SELECT COUNT(*) as count FROM road_defects")
    if cursor.fetchone()["count"] == 0:
        initial_defects = [
            ("pothole", 13.0569, 80.2425, "HIGH", 0.92, "lane_center", 4, "WORK_ORDER_ISSUED", "TKT-PWD-101"),
            ("waterlogging", 13.0102, 80.2157, "CRITICAL", 0.95, "lane_left", 6, "WORK_ORDER_ISSUED", "TKT-PWD-102"),
            ("missing_zebra_crossing", 13.0850, 80.2101, "MEDIUM", 0.88, "lane_center", 3, "REPORTED", None),
            ("damaged_road_divider", 12.9815, 80.2437, "HIGH", 0.89, "lane_right", 5, "WORK_ORDER_ISSUED", "TKT-PWD-103"),
            ("pothole", 13.0732, 80.2609, "MEDIUM", 0.84, "shoulder", 2, "REPORTED", None),
            ("damaged_traffic_sign", 12.9516, 80.2411, "LOW", 0.78, "shoulder", 1, "REPORTED", None)
        ]
        cursor.executemany("""
            INSERT INTO road_defects (hazard_type, latitude, longitude, severity, confidence, relative_position, confirmation_count, status, ticket_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, initial_defects)

        initial_tickets = [
            ("TKT-PWD-101", 1, "pothole", "Anna Salai near Thousand Lights", 13.0569, 80.2425, "HIGH", "HIGH", "OPEN"),
            ("TKT-PWD-102", 2, "waterlogging", "Guindy Underpass / Kathipara flyover", 13.0102, 80.2157, "CRITICAL", "CRITICAL", "OPEN"),
            ("TKT-PWD-103", 4, "damaged_road_divider", "Thiruvanmiyur Signal Junction", 12.9815, 80.2437, "HIGH", "HIGH", "IN_PROGRESS")
        ]
        cursor.executemany("""
            INSERT INTO maintenance_tickets (ticket_id, defect_id, defect_type, location_desc, latitude, longitude, severity, priority, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, initial_tickets)

        initial_incidents = [
            ("HIT_AND_RUN", "CRITICAL", "TN 09 BK 4591", 0.94, "{\"type\": \"SUV\", \"model\": \"Mahindra Scorpio\", \"color\": \"Black\"}", 84.5, 13.0418, 80.2341, "BUS-BEL-102", "TRK-9021", "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='320' height='180'><rect width='100%' height='100%' fill='%231e293b'/><text x='50%' y='40%' fill='%23ef4444' font-size='16' font-family='sans-serif' text-anchor='middle'>HIT AND RUN DETECTED</text><text x='50%' y='65%' fill='%23f8fafc' font-size='20' font-weight='bold' font-family='monospace' text-anchor='middle'>TN 09 BK 4591</text><text x='50%' y='85%' fill='%2394a3b8' font-size='12' font-family='sans-serif' text-anchor='middle'>Conf: 94% | Speed: 84.5 km/h</text></svg>", "ACTIVE"),
            ("RASH_DRIVING", "HIGH", "TN 01 CA 8823", 0.89, "{\"type\": \"Motorcycle\", \"model\": \"Bajaj Pulsar\", \"color\": \"Red\"}", 78.0, 13.0067, 80.2575, "BUS-BEL-105", "TRK-4412", "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='320' height='180'><rect width='100%' height='100%' fill='%231e293b'/><text x='50%' y='40%' fill='%23f59e0b' font-size='16' font-family='sans-serif' text-anchor='middle'>RASH DRIVING DETECTED</text><text x='50%' y='65%' fill='%23f8fafc' font-size='20' font-weight='bold' font-family='monospace' text-anchor='middle'>TN 01 CA 8823</text><text x='50%' y='85%' fill='%2394a3b8' font-size='12' font-family='sans-serif' text-anchor='middle'>Conf: 89% | Speed: 78.0 km/h</text></svg>", "ACTIVE")
        ]
        cursor.executemany("""
            INSERT INTO incident_alerts (incident_type, severity, license_plate, plate_confidence, vehicle_details, estimated_speed, latitude, longitude, reporting_bus_id, tracking_id, evidence_snapshot, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, initial_incidents)

        conn.commit()
    conn.close()
    print("[+] Baseline urban sensing and incident dataset seeded.")
