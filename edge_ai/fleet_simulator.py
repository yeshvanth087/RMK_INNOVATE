"""
Multi-Bus Fleet Telemetry & Edge AI Simulator.
Simulates autonomous sensing buses moving along realistic urban transport corridors.
Fires road hazards, traffic density variations, pedestrian alerts, and high-priority police incidents.
"""
import time
import math
import random
import requests
from typing import List, Dict, Any
from edge_ai.config import EdgeConfig
from edge_ai.detectors import (
    RoadHazardDetector,
    TrafficDensityCounter,
    PedestrianVRUDetector,
    ANPRIncidentTracker
)
from edge_ai.telemetry_packager import TelemetryPackager

# Curated real-world route waypoints (e.g. Chennai / Urban Metros)
SAMPLE_ROUTES = {
    "RT-101": {
        "name": "Central Station to Airport Express",
        "waypoints": [
            (13.0827, 80.2707),  # Central Station
            (13.0732, 80.2609),  # Egmore
            (13.0569, 80.2425),  # Thousand Lights / Anna Salai
            (13.0418, 80.2341),  # T. Nagar
            (13.0102, 80.2157),  # Guindy
            (12.9863, 80.1754),  # Meenambakkam
            (12.9941, 80.1709)   # Airport Terminal
        ]
    },
    "RT-204": {
        "name": "Marina Beach to IT Corridor (OMR)",
        "waypoints": [
            (13.0499, 80.2824),  # Marina Beach
            (13.0336, 80.2707),  # Mylapore
            (13.0067, 80.2575),  # Adyar
            (12.9815, 80.2437),  # Thiruvanmiyur
            (12.9516, 80.2411),  # Kandanchavadi / OMR
            (12.9249, 80.2312)   # Sholinganallur Hub
        ]
    },
    "RT-305": {
        "name": "North Ring Road to Koyambedu Hub",
        "waypoints": [
            (13.1147, 80.2872),  # Tondiarpet
            (13.1075, 80.2619),  # Basin Bridge
            (13.0850, 80.2101),  # Anna Nagar
            (13.0694, 80.1948)   # CMBT Koyambedu
        ]
    },
    "RT-410": {
        "name": "East-West Circular Link",
        "waypoints": [
            (13.0850, 80.2101),  # Anna Nagar
            (13.0612, 80.2285),  # Nungambakkam
            (13.0418, 80.2341),  # T. Nagar
            (13.0210, 80.2230)   # Saidapet
        ]
    }
}

# Known fixed ground-truth road hazard zones (simulating real-world potholes/waterlogging)
SIMULATED_HAZARD_ZONES = [
    {"lat": 13.0569, "lng": 80.2425, "type": "pothole", "severity": "HIGH", "desc": "Severe pothole cluster in middle lane"},
    {"lat": 13.0102, "lng": 80.2157, "type": "waterlogging", "severity": "CRITICAL", "desc": "Monsoon water accumulation under flyover"},
    {"lat": 13.0850, "lng": 80.2101, "type": "missing_zebra_crossing", "severity": "MEDIUM", "desc": "Faded pedestrian crossing near school"},
    {"lat": 12.9815, "lng": 80.2437, "type": "damaged_road_divider", "severity": "HIGH", "desc": "Broken median concrete barrier"},
    {"lat": 13.0732, "lng": 80.2609, "type": "pothole", "severity": "MEDIUM", "desc": "Surface erosion on bus bay"},
    {"lat": 12.9516, "lng": 80.2411, "type": "damaged_traffic_sign", "severity": "LOW", "desc": "Tilted speed limit signboard"}
]

class BusFleetSimulator:
    def __init__(self, num_buses: int = 8, backend_url: str = "http://127.0.0.1:8000/api/telemetry/ping"):
        self.backend_url = backend_url
        self.hazard_detector = RoadHazardDetector()
        self.traffic_counter = TrafficDensityCounter()
        self.vru_detector = PedestrianVRUDetector()
        self.anpr_tracker = ANPRIncidentTracker()
        
        self.buses = []
        route_keys = list(SAMPLE_ROUTES.keys())
        for i in range(num_buses):
            route_id = route_keys[i % len(route_keys)]
            self.buses.append({
                "bus_id": f"BUS-BEL-{101 + i}",
                "route_id": route_id,
                "current_step": random.uniform(0, len(SAMPLE_ROUTES[route_id]["waypoints"]) - 1),
                "speed_kmh": random.uniform(18.0, 38.0),
                "crowding_pct": random.uniform(20.0, 85.0),
                "heading": random.uniform(0, 360)
            })

    def interpolate_position(self, route_id: str, step_val: float) -> tuple[float, float, float]:
        """Calculates interpolated lat, lng and heading along waypoints."""
        waypoints = SAMPLE_ROUTES[route_id]["waypoints"]
        idx = int(step_val) % (len(waypoints) - 1)
        fraction = step_val - int(step_val)
        
        p1 = waypoints[idx]
        p2 = waypoints[idx + 1]
        
        lat = p1[0] + (p2[0] - p1[0]) * fraction
        lng = p1[1] + (p2[1] - p1[1]) * fraction
        
        # Calculate heading
        d_lat = p2[0] - p1[0]
        d_lng = p2[1] - p1[1]
        heading = (math.atan2(d_lng, d_lat) * 180 / math.pi) % 360
        
        return lat, lng, heading

    def step(self, trigger_police_incident: bool = False) -> List[Dict[str, Any]]:
        """Advances each bus by one simulation step and returns generated payloads."""
        generated_payloads = []
        
        for bus in self.buses:
            # Advance along route
            step_increment = 0.04 * (bus["speed_kmh"] / 30.0)
            bus["current_step"] = (bus["current_step"] + step_increment) % (len(SAMPLE_ROUTES[bus["route_id"]]["waypoints"]) - 1)
            
            lat, lng, heading = self.interpolate_position(bus["route_id"], bus["current_step"])
            bus["heading"] = heading
            
            # Fluctuating speed with traffic context
            bus["speed_kmh"] = max(8.0, min(50.0, bus["speed_kmh"] + random.uniform(-4.0, 4.0)))
            
            # Check proximity to known simulated hazard zones
            detected_hazards = []
            for h in SIMULATED_HAZARD_ZONES:
                dist = math.sqrt((lat - h["lat"])**2 + (lng - h["lng"])**2)
                if dist < 0.003: # Near hazard zone
                    hazard_meta = {
                        "has_hazard": True,
                        "hazard_type": h["type"],
                        "severity": h["severity"]
                    }
                    detected_hazards.extend(self.hazard_detector.detect_hazards(hazard_meta))
            
            # If no fixed hazard, small random chance of defect
            if not detected_hazards and random.random() < 0.05:
                detected_hazards.extend(self.hazard_detector.detect_hazards({"has_hazard": True}))

            # Traffic density estimation
            traffic_data = self.traffic_counter.estimate_density(bus["speed_kmh"])
            
            # Pedestrian VRU check
            is_school = "13.0850" in f"{lat:.4f}" or random.random() < 0.1
            vru_alerts = self.vru_detector.evaluate_pedestrian_safety(is_school_zone=is_school)
            
            # Incident / ANPR check
            incident_data = None
            if trigger_police_incident or random.random() < 0.03:
                inc_type = random.choice(["HIT_AND_RUN", "RASH_DRIVING", "OVER_SPEEDING"])
                incident_data = self.anpr_tracker.evaluate_incident(inc_type)

            # Compile into Edge Telemetry Payload
            payload = TelemetryPackager.create_payload(
                bus_id=bus["bus_id"],
                route_id=bus["route_id"],
                latitude=lat,
                longitude=lng,
                speed_kmh=bus["speed_kmh"],
                heading_deg=bus["heading"],
                hazards=detected_hazards,
                traffic=traffic_data,
                vru_alerts=vru_alerts,
                incident=incident_data,
                passenger_crowding_pct=bus["crowding_pct"]
            )
            generated_payloads.append(payload)
            
        return generated_payloads

    def run_continuous_stream(self, interval_seconds: float = 3.0):
        """Continuously sends pings to the FastAPI server."""
        print(f"[*] Starting NeuroNex UrbanSense Fleet Simulator with {len(self.buses)} buses...")
        print(f"[*] Streaming telemetry to: {self.backend_url}")
        
        step_count = 0
        while True:
            step_count += 1
            trigger_incident = (step_count % 10 == 0) # Trigger an incident every 10 ticks
            payloads = self.step(trigger_police_incident=trigger_incident)
            
            for p in payloads:
                try:
                    res = requests.post(self.backend_url, json=p, timeout=2.0)
                    if p["incident"]:
                        print(f" [!] INCIDENT DISPATCHED from {p['bus_id']}: {p['incident']['incident_type']} | Plate: {p['incident']['license_plate']}")
                except Exception as e:
                    # Backend may be starting up
                    pass
                    
            time.sleep(interval_seconds)

if __name__ == "__main__":
    sim = BusFleetSimulator(num_buses=8)
    sim.run_continuous_stream(interval_seconds=3.0)
