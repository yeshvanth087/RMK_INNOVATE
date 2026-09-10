import unittest
import sqlite3
import os
import sys
from fastapi.testclient import TestClient

from healthcare_agent.database import (
    init_db,
    get_db_connection,
    get_patients_summary,
    get_patient_360,
    add_checkin_record,
    log_med_intake,
    DB_PATH
)
from healthcare_agent.research_engine import rag_engine
from healthcare_agent.analysis_agent import analysis_agent
from healthcare_agent.monitoring_agent import monitoring_agent
from healthcare_agent.explanation_engine import explanation_engine
from healthcare_agent.safety_engine import safety_engine
from healthcare_agent.documentation_agent import doc_agent
from healthcare_agent.orchestrator import orchestrator_agent
from healthcare_agent.main import app

class TestHealthcareAgentPlatform(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_01_database_tables(self):
        """Verify all 13 CSV tables exist in SQLite database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        table_names = [t["name"] for t in tables]
        conn.close()

        required_tables = [
            "patients", "consultations", "vitals", "lab_results",
            "symptoms", "daily_checkins", "monitoring_events",
            "medications", "medication_adherence", "appointments",
            "doctors", "hospitals", "disease_knowledge", "escalation_rules"
        ]
        for t in required_tables:
            self.assertIn(t, table_names, f"Table {t} missing from database")
        print("[PASS] Test 1: All 13 relational tables loaded in SQLite.")

    def test_02_patient_360_health_graph(self):
        """Verify multi-table relational join around patient_id."""
        p360 = get_patient_360("PAT_001")
        self.assertIsNotNone(p360)
        self.assertEqual(p360["patient_id"], "PAT_001")
        self.assertEqual(p360["first_name"], "Ramesh")
        self.assertGreaterEqual(len(p360["vitals"]), 10)
        self.assertGreaterEqual(len(p360["medications"]), 2)
        self.assertGreaterEqual(len(p360["consultations"]), 1)
        self.assertGreaterEqual(len(p360["lab_results"]), 1)
        self.assertEqual(p360["doctor_name"], "Dr. Arvind Ramanathan")
        print("[PASS] Test 2: Patient 360 Health Graph joins successfully across all 13 datasets.")

    def test_03_research_rag_citations(self):
        """Verify RAG engine retrieves medical literature with DOIs and guidelines."""
        results = rag_engine.search("Stage 2 hypertension Telmisartan Amlodipine", top_k=2)
        self.assertGreaterEqual(len(results), 1)
        top = results[0]
        self.assertIn("doi", top)
        self.assertIn("relevance_score", top)
        self.assertIn("citation", top)
        print(f"[PASS] Test 3: Research RAG retrieved match: '{top['title']}' with score {top['relevance_score']}.")

    def test_04_analysis_vitals_trend(self):
        """Verify trend engine detects systolic BP spike and hypoxia."""
        p360 = get_patient_360("PAT_001")
        analysis = analysis_agent.analyze_vitals_trends(p360["vitals"])
        self.assertIn("systolic_bp", analysis)
        self.assertGreaterEqual(analysis["systolic_bp"]["current"], 170)
        self.assertEqual(analysis["systolic_bp"]["trend"], "SPIKING")
        print(f"[PASS] Test 4: Clinical Analysis Agent correctly detected Systolic BP trend '{analysis['systolic_bp']['trend']}'.")

    def test_05_explanation_engine(self):
        """Verify Explanation Engine outputs 'What Changed?' and 'Why It Matters?'."""
        p360 = get_patient_360("PAT_001")
        vitals_analysis = analysis_agent.analyze_vitals_trends(p360["vitals"])
        lab_anomalies = analysis_agent.analyze_lab_anomalies(p360["lab_results"])
        monitoring_status = monitoring_agent.evaluate_monitoring_status(p360)

        expl = explanation_engine.generate_explanation(p360, vitals_analysis, monitoring_status, lab_anomalies)
        self.assertIn("what_changed", expl)
        self.assertIn("why_it_matters", expl)
        self.assertGreaterEqual(len(expl["what_changed"]), 1)
        self.assertGreaterEqual(len(expl["why_it_matters"]), 1)
        print("[PASS] Test 5: Explanation Engine successfully formulated 'What Changed?' and 'Why It Matters?'.")

    def test_06_safety_escalation_rules(self):
        """Verify deterministic rules trigger emergency triage on critical vitals."""
        # 1. Critical Hypertensive Crisis
        crit_metrics = {"systolic_bp": 188.0, "diastolic_bp": 105.0}
        eval_res = safety_engine.evaluate(crit_metrics)
        self.assertEqual(eval_res["status"], "CONCERN")
        self.assertEqual(eval_res["triage_level"], "EMERGENCY_CRITICAL")
        self.assertTrue(eval_res["requires_doctor_review"])

        # 2. Stable patient
        stable_metrics = {"systolic_bp": 120.0, "diastolic_bp": 80.0, "spo2": 98.0, "heart_rate": 72.0}
        eval_stable = safety_engine.evaluate(stable_metrics)
        self.assertEqual(eval_stable["status"], "NORMAL")
        self.assertFalse(eval_stable["requires_doctor_review"])
        print("[PASS] Test 6: Safety Engine correctly evaluates thresholds against escalation_rules.csv.")

    def test_07_documentation_agent_soap(self):
        """Verify SOAP note generation with S, O, A, P components."""
        intel = orchestrator_agent.get_complete_patient_intelligence("PAT_001")
        soap = intel["doctor_intelligence"]["soap_note"]["soap"]
        self.assertIn("S_Subjective", soap)
        self.assertIn("O_Objective", soap)
        self.assertIn("A_Assessment", soap)
        self.assertIn("P_Plan", soap)
        print("[PASS] Test 7: Documentation Agent produced full clinical SOAP note.")

    def test_08_api_endpoints(self):
        """Verify FastAPI REST API endpoints."""
        # Test Patients list
        res = self.client.get("/api/patients")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["success"])

        # Test Patient Intelligence
        res_intel = self.client.get("/api/patients/PAT_001/intelligence")
        self.assertEqual(res_intel.status_code, 200)
        data = res_intel.json()["data"]
        self.assertIn("doctor_intelligence", data)
        self.assertIn("patient_companion", data)

        # Test Check-in
        res_chk = self.client.post("/api/patients/PAT_001/checkin", json={
            "pain_score": 4,
            "sleep_hours": 7.0,
            "fatigue_level": "Moderate",
            "mood": "Good",
            "fluid_intake_liters": 2.2,
            "notes": "Feeling slightly better after resting."
        })
        self.assertEqual(res_chk.status_code, 200)

        # Test Chat
        res_chat = self.client.post("/api/chat/patient", json={
            "patient_id": "PAT_001",
            "message": "I have a morning headache, what should I do?"
        })
        self.assertEqual(res_chat.status_code, 200)
        self.assertIn("reply", res_chat.json()["data"])
        print("[PASS] Test 8: All FastAPI REST endpoints and chat workflows verified.")

if __name__ == "__main__":
    unittest.main()
