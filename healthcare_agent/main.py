import os
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from .database import (
    init_db,
    get_patients_summary,
    get_patient_360,
    add_checkin_record,
    log_med_intake
)
from .orchestrator import orchestrator_agent
from .research_engine import rag_engine
from .safety_engine import safety_engine

app = FastAPI(
    title="AI-Powered Healthcare Research & Patient Support Agent",
    description="Agentic Healthcare Platform for Clinical Decision Support, Research RAG, and Patient Daily Companion",
    version="1.0.0"
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Models
class CheckinPayload(BaseModel):
    pain_score: int
    sleep_hours: float
    fatigue_level: str
    mood: str
    fluid_intake_liters: float
    notes: Optional[str] = ""

class MedIntakePayload(BaseModel):
    medication_id: str

class ChatPayload(BaseModel):
    patient_id: str
    message: str

# Static Files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Healthcare AI Agent API is online. Static UI not yet deployed."}

# API Endpoints
@app.get("/api/patients")
def list_patients():
    """Returns patient roster with baseline conditions and active risk tiers."""
    patients = get_patients_summary()
    return {"success": True, "count": len(patients), "patients": patients}

@app.get("/api/patients/{patient_id}/intelligence")
def get_patient_intelligence(patient_id: str):
    """
    Runs full Multi-Agent Orchestrator pipeline:
    Health Graph -> Analysis Agent -> Monitoring Agent -> Explanations -> Safety Engine -> Research RAG -> SOAP Note
    """
    data = orchestrator_agent.get_complete_patient_intelligence(patient_id)
    if not data:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"success": True, "data": data}

@app.post("/api/patients/{patient_id}/checkin")
def submit_checkin(patient_id: str, payload: CheckinPayload):
    """Logs daily check-in and re-evaluates patient care status."""
    chk_id = add_checkin_record(
        patient_id=patient_id,
        pain_score=payload.pain_score,
        sleep_hours=payload.sleep_hours,
        fatigue=payload.fatigue_level,
        mood=payload.mood,
        fluid=payload.fluid_intake_liters,
        notes=payload.notes or ""
    )
    return {"success": True, "checkin_id": chk_id, "message": "Daily check-in logged successfully."}

@app.post("/api/patients/{patient_id}/medication/take")
def take_medication(patient_id: str, payload: MedIntakePayload):
    """Marks dose as taken and recalculates adherence score."""
    log_med_intake(patient_id, payload.medication_id)
    return {"success": True, "message": f"Dose logged for medication {payload.medication_id}."}

@app.post("/api/chat/patient")
def chat_patient_companion(payload: ChatPayload):
    """Handles empathetic patient companion conversation with guardrails."""
    res = orchestrator_agent.process_patient_chat(payload.patient_id, payload.message)
    return {"success": True, "data": res}

@app.post("/api/chat/doctor")
def chat_doctor_copilot(payload: ChatPayload):
    """Handles clinical decision support and research verification for physicians."""
    res = orchestrator_agent.process_doctor_chat(payload.patient_id, payload.message)
    return {"success": True, "data": res}

@app.get("/api/research/search")
def search_medical_research(query: str, top_k: int = 3):
    """Direct semantic RAG search across medical research chunks and disease ontology."""
    results = rag_engine.search(query, top_k=top_k)
    return {"success": True, "query": query, "count": len(results), "results": results}

@app.get("/api/safety/alerts")
def get_live_escalation_worklist():
    """Aggregates all patients currently breaching critical or warning safety thresholds."""
    patients = get_patients_summary()
    alerts = []
    for p in patients:
        intel = orchestrator_agent.get_complete_patient_intelligence(p["patient_id"])
        if intel:
            doc_intel = intel["doctor_intelligence"]
            if doc_intel["requires_doctor_review"]:
                alerts.append({
                    "patient_id": p["patient_id"],
                    "patient_name": f"{p['first_name']} {p['last_name']}",
                    "condition": p["primary_condition"],
                    "triage_level": doc_intel["triage_level"],
                    "safety_alerts": doc_intel["safety_alerts"]
                })
    return {"success": True, "count": len(alerts), "alerts": alerts}
