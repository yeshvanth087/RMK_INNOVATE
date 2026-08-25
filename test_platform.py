"""
Automated Test Suite for NeuroNex UrbanSense AI Platform
Tests Edge Detectors, Spatial Deduplication, ML Analytics, Detour Solver, and API Endpoints.
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from edge_ai.detectors import (
    RoadHazardDetector,
    TrafficDensityCounter,
    PedestrianVRUDetector,
    ANPRIncidentTracker
)
from edge_ai.telemetry_packager import TelemetryPackager
from backend.app.database import init_db, get_db_connection
from backend.app.services.spatial_clustering import SpatialClusteringService
from backend.app.services.delay_predictor import delay_service
from backend.app.services.route_optimizer import route_optimizer
from backend.app.services.gtfs_analyzer import gtfs_analyzer
from backend.app.services.decision_assistant import decision_assistant

class TestUrbanSensePlatform(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_01_road_hazard_detector(self):
        detector = RoadHazardDetector(confidence_threshold=0.6)
        meta = {"has_hazard": True, "hazard_type": "pothole", "severity": "HIGH"}
        hazards = detector.detect_hazards(meta)
        self.assertGreater(len(hazards), 0)
        self.assertEqual(hazards[0]["type"], "pothole")
        self.assertEqual(hazards[0]["severity"], "HIGH")
        self.assertGreaterEqual(hazards[0]["confidence"], 0.6)
        print("[PASS] Test 01 Passed: Road Hazard Detector")

    def test_02_traffic_density_counter(self):
        counter = TrafficDensityCounter()
        density_slow = counter.estimate_density(current_speed_kmh=8.0)
        self.assertIn("vehicle_counts", density_slow)
        self.assertGreater(density_slow["total_pcu"], 20.0)
        self.assertTrue(density_slow["density_level"] in ["HEAVY", "CRITICAL_BOTTLENECK"])
        print("[PASS] Test 02 Passed: Traffic Density & PCU Counter")

    def test_03_pedestrian_vru_detector(self):
        vru = PedestrianVRUDetector()
        alerts = vru.evaluate_pedestrian_safety(is_school_zone=True)
        self.assertIsInstance(alerts, list)
        print("[PASS] Test 03 Passed: Pedestrian VRU Detector")

    def test_04_anpr_incident_tracker(self):
        tracker = ANPRIncidentTracker()
        incident = tracker.evaluate_incident("HIT_AND_RUN")
        self.assertIsNotNone(incident)
        self.assertEqual(incident["incident_type"], "HIT_AND_RUN")
        self.assertEqual(incident["severity"], "CRITICAL")
        self.assertTrue(len(incident["license_plate"]) > 5)
        self.assertGreaterEqual(incident["plate_confidence"], 0.75)
        print(f"[PASS] Test 04 Passed: ANPR Plate Extraction -> {incident['license_plate']}")

    def test_05_telemetry_packager_bandwidth(self):
        payload = TelemetryPackager.create_payload(
            bus_id="BUS-BEL-101",
            route_id="RT-101",
            latitude=13.0827,
            longitude=80.2707,
            speed_kmh=25.0,
            heading_deg=180.0,
            hazards=[{"type": "pothole", "severity": "HIGH", "confidence": 0.9}],
            traffic={"total_pcu": 24.5, "density_level": "MODERATE", "is_bottleneck": False},
            vru_alerts=[]
        )
        size_bytes = TelemetryPackager.get_payload_size_bytes(payload)
        self.assertLess(size_bytes, 2048, "Payload should be lightweight (< 2KB) for 4G/5G edge constraints")
        print(f"[PASS] Test 05 Passed: Edge Payload Packaging ({size_bytes} bytes)")

    def test_06_spatial_deduplication(self):
        # First bus reports pothole
        res1 = SpatialClusteringService.process_hazard_ping("pothole", 13.045000, 80.231000, "HIGH", 0.88)
        self.assertIn(res1["action"], ["CREATED", "MERGED"])
        
        # Second bus passes 8 meters away
        res2 = SpatialClusteringService.process_hazard_ping("pothole", 13.045050, 80.231040, "HIGH", 0.94)
        self.assertEqual(res2["action"], "MERGED")
        self.assertGreaterEqual(res2["confirmation_count"], 2)
        print(f"[PASS] Test 06 Passed: Spatial Deduplication merged duplicate pings (Count: {res2['confirmation_count']})")

    def test_07_ml_delay_predictor(self):
        pred = delay_service.predict_route_delay(route_id="RT-101", hour=18, weather="HEAVY_RAIN", crowding_pct=80.0)
        self.assertIn("predicted_delay_minutes", pred)
        self.assertGreater(pred["predicted_delay_minutes"], 5.0)
        print(f"[PASS] Test 07 Passed: ML Delay Prediction -> +{pred['predicted_delay_minutes']} mins ({pred['delay_category']})")

    def test_08_dynamic_route_detour(self):
        route = route_optimizer.calculate_optimized_route("NODE_CENTRAL", "NODE_AIRPORT", avoid_critical_hazards=True)
        self.assertIn("status", route)
        self.assertGreater(len(route["route_waypoints"]), 3)
        print(f"[PASS] Test 08 Passed: Dynamic Detour Solver -> {route['status']} (Saved: {route['estimated_time_saved_min']} mins)")

    def test_09_decision_assistant_query(self):
        ans = decision_assistant.query("Show high severity potholes")
        self.assertEqual(ans["domain"], "MUNICIPAL_PWD")
        self.assertTrue("defect" in ans["summary"].lower() or "pothole" in ans["summary"].lower())
        print(f"[PASS] Test 09 Passed: AI Decision Assistant NLP Query -> {ans['domain']}")

    def test_10_gtfs_corridor_kpis(self):
        kpis = gtfs_analyzer.get_system_summary_kpis()
        self.assertGreaterEqual(kpis["active_sensing_buses"], 8)
        self.assertGreaterEqual(kpis["urban_roads_scanned_km"], 100.0)
        print(f"[PASS] Test 10 Passed: GTFS Corridor Analytics -> {kpis['active_sensing_buses']} active sensing buses")

if __name__ == "__main__":
    unittest.main(verbosity=2)
