"""
Database engine and geospatial math utilities.
Uses SQLite with optimized spatial indexing and Haversine distance computations.
"""
import sqlite3
import math
import os
from typing import Tuple, List, Dict, Any

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "urbansense.db")

def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes accurate great-circle distance between two GPS coordinates in meters.
    """
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def init_db():
    """Initializes the database schema if not already present."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Bus Live Telemetry Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bus_telemetry (
        bus_id TEXT PRIMARY KEY,
        route_id TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        speed_kmh REAL NOT NULL,
        heading_deg REAL NOT NULL,
        crowding_pct REAL NOT NULL,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Road Hazards & Defects Master Table (Spatially Deduplicated)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS road_defects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hazard_type TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        severity TEXT NOT NULL,
        confidence REAL NOT NULL,
        relative_position TEXT,
        confirmation_count INTEGER DEFAULT 1,
        status TEXT DEFAULT 'REPORTED', -- 'REPORTED', 'WORK_ORDER_ISSUED', 'REPAIRED', 'VERIFIED'
        ticket_id TEXT,
        first_detected DATETIME DEFAULT CURRENT_TIMESTAMP,
        last_confirmed DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 3. Police Incidents & ANPR Alert Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS incident_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        license_plate TEXT,
        plate_confidence REAL,
        vehicle_details TEXT,
        estimated_speed REAL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        reporting_bus_id TEXT,
        tracking_id TEXT,
        evidence_snapshot TEXT,
        status TEXT DEFAULT 'ACTIVE', -- 'ACTIVE', 'DISPATCHED', 'RESOLVED'
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 4. PWD Maintenance Tickets
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maintenance_tickets (
        ticket_id TEXT PRIMARY KEY,
        defect_id INTEGER,
        defect_type TEXT NOT NULL,
        location_desc TEXT,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        severity TEXT NOT NULL,
        priority TEXT NOT NULL, -- 'HIGH', 'CRITICAL', 'NORMAL'
        assigned_department TEXT DEFAULT 'PWD Road Maintenance Wing',
        status TEXT DEFAULT 'OPEN', -- 'OPEN', 'IN_PROGRESS', 'RESOLVED', 'AI_VERIFIED'
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 5. Traffic Congestion Hotspots Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS traffic_hotspots (
        corridor_id TEXT PRIMARY KEY,
        route_id TEXT NOT NULL,
        segment_name TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        total_pcu REAL NOT NULL,
        density_level TEXT NOT NULL,
        avg_speed_kmh REAL NOT NULL,
        is_bottleneck INTEGER NOT NULL,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
    print("[+] SQLite UrbanSense database initialized successfully.")

# Run initialization on import
init_db()
