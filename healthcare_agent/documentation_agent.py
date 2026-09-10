import pandas as pd
from typing import Dict, Any, List

class DocumentationAgent:
    """
    Creates structured clinical SOAP notes (Subjective, Objective, Assessment, Plan),
    discharge summaries, and digital documentation directly from the health graph.
    """

    def generate_soap_note(self, patient_360: Dict[str, Any], explanation: Dict[str, Any], evidence_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        p = patient_360
        vitals = p.get("vitals", [])
        latest_vital = vitals[-1] if vitals else {}
        symptoms = p.get("symptoms", [])
        recent_symptom = symptoms[0] if symptoms else {}
        checkins = p.get("daily_checkins", [])
        recent_checkin = checkins[0] if checkins else {}
        meds = p.get("medications", [])
        labs = p.get("lab_results", [])
        consults = p.get("consultations", [])
        last_consult = consults[0] if consults else {}

        # 1. Subjective (S)
        subjective = {
            "chief_complaint": recent_symptom.get("symptom_name", last_consult.get("chief_complaint", "Routine follow-up.")),
            "symptom_severity": f"{recent_symptom.get('severity', 'N/A')} / 10" if recent_symptom else "Mild",
            "patient_reported_pain": f"{recent_checkin.get('pain_score', 0)} / 10",
            "sleep_quality": f"{recent_checkin.get('sleep_hours', 7.0)} hrs/night, Fatigue: {recent_checkin.get('fatigue_level', 'Normal')}",
            "patient_notes": recent_checkin.get("notes", "Compliance maintained with prescribed care plan.")
        }

        # 2. Objective (O)
        objective = {
            "vital_signs": {
                "blood_pressure": f"{latest_vital.get('systolic_bp', '--')}/{latest_vital.get('diastolic_bp', '--')} mmHg",
                "heart_rate": f"{latest_vital.get('heart_rate', '--')} bpm",
                "spo2": f"{latest_vital.get('spo2', '--')}%",
                "temperature": f"{latest_vital.get('temperature_c', '--')} °C",
                "blood_glucose": f"{latest_vital.get('blood_glucose_mg_dl', '--')} mg/dL",
                "respiratory_rate": f"{latest_vital.get('respiratory_rate', '--')} bpm",
                "recorded_at": latest_vital.get("recorded_at", "N/A")
            },
            "recent_lab_biomarkers": [
                f"{l['biomarker']}: {l['result_value']} {l['unit']} ({l['status']})" for l in labs[:4]
            ],
            "current_medications": [
                f"{m['medication_name']} {m['dosage']} ({m['frequency']}) - Adherence: {m.get('adherence_rate', 100)}%" for m in meds
            ]
        }

        # 3. Assessment (A)
        assessment = {
            "primary_diagnosis": p.get("primary_condition", "Under Clinical Evaluation"),
            "risk_tier": p.get("risk_tier", "MODERATE"),
            "what_changed": explanation.get("what_changed", []),
            "pathophysiological_rationale": explanation.get("why_it_matters", [])
        }

        # 4. Plan (P)
        evidence_citations = [e["citation"] for e in evidence_list[:2]] if evidence_list else []
        plan = {
            "pharmacological_recommendations": [
                f"Continue active regimen with strict adherence oversight.",
                f"Evaluate dose titration if blood pressure or glucose parameters remain out of target range."
            ],
            "monitoring_orders": [
                "Bi-daily home vital logging (morning & evening)",
                "Review daily check-ins for sudden symptoms escalation"
            ],
            "patient_education_and_precautions": [
                "Reinforce dietary restrictions and hydration limits",
                "Maintain seamless foot inspection and trigger emergency SOS on red flags"
            ],
            "evidence_base": evidence_citations
        }

        return {
            "patient_id": p.get("patient_id"),
            "patient_name": f"{p.get('first_name')} {p.get('last_name')}",
            "generated_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "soap": {
                "S_Subjective": subjective,
                "O_Objective": objective,
                "A_Assessment": assessment,
                "P_Plan": plan
            }
        }

doc_agent = DocumentationAgent()
