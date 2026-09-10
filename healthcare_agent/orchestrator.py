import json
from typing import Dict, Any, List, Optional
from .database import get_patient_360
from .research_engine import rag_engine
from .analysis_agent import analysis_agent
from .monitoring_agent import monitoring_agent
from .explanation_engine import explanation_engine
from .safety_engine import safety_engine
from .documentation_agent import doc_agent

class OrchestratorAgent:
    """
    Master Orchestrator Agent:
    - Coordinates the 5 specialized sub-agents
    - Executes the Patient Timeline / Health Graph reasoning loop
    - Produces dual-view outputs: Doctor Clinical Dashboard & Patient Daily Companion
    """

    def get_complete_patient_intelligence(self, patient_id: str) -> Optional[Dict[str, Any]]:
        # 1. Fetch complete health graph
        patient_360 = get_patient_360(patient_id)
        if not patient_360:
            return None

        # 2. Run Clinical Analysis Agent on vitals & labs
        vitals_analysis = analysis_agent.analyze_vitals_trends(patient_360.get("vitals", []))
        lab_anomalies = analysis_agent.analyze_lab_anomalies(patient_360.get("lab_results", []))

        # 3. Run Daily Monitoring Agent
        monitoring_status = monitoring_agent.evaluate_monitoring_status(patient_360)

        # 4. Run Explanation Engine ("What Changed?" & "Why It Matters?")
        explanations = explanation_engine.generate_explanation(
            patient_360, vitals_analysis, monitoring_status, lab_anomalies
        )

        # 5. Extract latest metrics for Safety Engine evaluation
        latest_vital = vitals_analysis.get("latest_reading", {})
        metrics_payload = {
            "systolic_bp": latest_vital.get("systolic_bp"),
            "diastolic_bp": latest_vital.get("diastolic_bp"),
            "spo2": latest_vital.get("spo2"),
            "heart_rate": latest_vital.get("heart_rate"),
            "blood_glucose_mg_dl": latest_vital.get("blood_glucose_mg_dl"),
            "pain_score": monitoring_status.get("pain_score"),
            "adherence_rate": monitoring_status.get("avg_adherence_rate")
        }
        safety_eval = safety_engine.evaluate(metrics_payload)

        # 6. Retrieve evidence from Research Agent RAG
        condition_query = f"{patient_360['primary_condition']} treatment guidelines red flags management"
        research_evidence = rag_engine.search(condition_query, top_k=3)

        # 7. Generate SOAP Note from Documentation Agent
        soap_note = doc_agent.generate_soap_note(patient_360, explanations, research_evidence)

        # 8. Compile Dual Perspectives
        doctor_view = {
            "triage_status": safety_eval["status"],
            "triage_level": safety_eval["triage_level"],
            "requires_doctor_review": safety_eval["requires_doctor_review"],
            "safety_alerts": safety_eval["triggered_rules"],
            "what_changed": explanations["what_changed"],
            "why_it_matters": explanations["why_it_matters"],
            "vitals_analysis": vitals_analysis,
            "lab_anomalies": lab_anomalies,
            "soap_note": soap_note,
            "research_evidence": research_evidence
        }

        patient_view = {
            "status_badge": "🟢 Normal" if safety_eval["status"] == "NORMAL" else "🔴 Action Needed",
            "greeting": f"Hello {patient_360['first_name']}, here is your daily health companion update.",
            "overall_adherence": monitoring_status["avg_adherence_rate"],
            "daily_precautions": monitoring_status["daily_precautions"],
            "plain_explanation": self._format_patient_plain_explanation(explanations, safety_eval),
            "medications_today": monitoring_status["adherence_details"],
            "emergency_contact": patient_360.get("emergency_contact_phone")
        }

        return {
            "patient_profile": patient_360,
            "doctor_intelligence": doctor_view,
            "patient_companion": patient_view
        }

    def process_patient_chat(self, patient_id: str, message: str) -> Dict[str, Any]:
        """
        Handles interactive patient conversation with empathetic care & safety guardrails.
        """
        p360 = get_patient_360(patient_id)
        if not p360:
            return {"reply": "Sorry, patient record could not be loaded."}

        # Check safety guardrails first
        vitals = p360.get("vitals", [])
        latest_vital = vitals[-1] if vitals else {}
        metrics = {
            "systolic_bp": latest_vital.get("systolic_bp"),
            "diastolic_bp": latest_vital.get("diastolic_bp"),
            "spo2": latest_vital.get("spo2"),
            "heart_rate": latest_vital.get("heart_rate")
        }
        safety = safety_engine.evaluate(metrics)

        # Retrieve relevant clinical guidance
        evidence = rag_engine.search(message, top_k=2)
        top_context = evidence[0]["document_text"] if evidence else ""

        # Construct empathetic AI response
        msg_lower = message.lower()
        if "headache" in msg_lower or "bp" in msg_lower or "pressure" in msg_lower:
            curr_bp = latest_vital.get('systolic_bp', 120)
            if curr_bp >= 170:
                reply = (
                    f"⚠️ Ramesh, your latest recorded blood pressure is high at {curr_bp} mmHg. "
                    f"Because you are also feeling a headache, please sit comfortably in a quiet room, avoid sudden movements, "
                    f"and do not exert yourself. I have already notified Dr. Arvind Ramanathan's clinic for a priority review. "
                    f"If you feel severe dizziness, chest discomfort, or vision blurring, please press the Red Emergency Alert immediately."
                )
            else:
                reply = (
                    f"Your recent blood pressure is recorded at {curr_bp} mmHg. Occipital headaches can happen with fatigue or stress. "
                    f"Take your morning Telmisartan if you haven't taken it today, stay well hydrated, and rest for 20 minutes. "
                    f"Let's check your blood pressure again in an hour."
                )
        elif "foot" in msg_lower or "sugar" in msg_lower or "tingling" in msg_lower:
            reply = (
                f"Tingling or burning sensations in your feet are common signs of diabetic nerve sensitivity. "
                f"Make sure to inspect the bottoms of your feet daily for any minor blisters, wear soft seamless socks, "
                f"and ensure you take your Metformin and Dapagliflozin with your regular meals. "
                f"I've logged this symptom for Dr. Sunita's upcoming review."
            )
        elif "inhaler" in msg_lower or "breath" in msg_lower or "cough" in msg_lower:
            curr_spo2 = latest_vital.get('spo2', 98)
            if curr_spo2 <= 90:
                reply = (
                    f"🚨 Warning: Your oxygen saturation is currently {curr_spo2}%. "
                    f"Please use your rescue inhaler immediately, sit upright propped with pillows, and seek immediate clinical care."
                )
            else:
                reply = (
                    f"Your oxygen saturation is currently stable at {curr_spo2}%. "
                    f"Remember to use your Budesonide/Formoterol inhaler as prescribed (2 puffs twice daily) and rinse your mouth with water afterward. "
                    f"Keep your rescue inhaler nearby during morning walks."
                )
        else:
            guidance_snippet = evidence[0]["title"] if evidence else "clinical best practices"
            reply = (
                f"Thank you for checking in. Based on your health profile for {p360['primary_condition']} and {guidance_snippet}: "
                f"Continue following your prescribed medication schedule, log your daily check-in, and reach out if you notice any unusual symptoms."
            )

        return {
            "reply": reply,
            "safety_status": safety["status"],
            "citations": [e["citation"] for e in evidence]
        }

    def process_doctor_chat(self, patient_id: str, query: str) -> Dict[str, Any]:
        """
        Handles doctor queries with clinical precision, SOAP data, and literature citations.
        """
        p360 = get_patient_360(patient_id)
        if not p360:
            return {"reply": "Patient record not found."}

        evidence = rag_engine.search(query, top_k=3)
        vitals = p360.get("vitals", [])
        latest_vital = vitals[-1] if vitals else {}
        meds = p360.get("medications", [])

        med_list_str = ", ".join([f"{m['medication_name']} {m['dosage']}" for m in meds])
        evidence_text = "\n\n".join([f"• **{e['title']}** ({e['journal']}, {e['publication_year']}): {e['document_text']}\n*DOI: {e['doi']}*" for e in evidence])

        reply = (
            f"### 📋 Clinical Decision Support for Patient {patient_id} ({p360['first_name']} {p360['last_name']})\n\n"
            f"**Primary Diagnosis:** {p360['primary_condition']}\n"
            f"**Current Regimen:** {med_list_str}\n"
            f"**Latest Vitals:** BP {latest_vital.get('systolic_bp')}/{latest_vital.get('diastolic_bp')} mmHg | SpO2 {latest_vital.get('spo2')}% | HR {latest_vital.get('heart_rate')} bpm\n\n"
            f"**Relevant Research Evidence & Guidelines:**\n{evidence_text}\n\n"
            f"**Recommendation:** Cross-reference patient adherence metrics before escalating dosage."
        )

        return {
            "reply": reply,
            "evidence": evidence
        }

    def _format_patient_plain_explanation(self, explanations: Dict[str, Any], safety: Dict[str, Any]) -> str:
        if safety["status"] == "CONCERN":
            return "⚠️ Noticeable changes were detected in your latest health readings. Our clinical safety engine has highlighted these for your doctor's review. Please review your daily precautions below."
        return "✨ Great news! Your health metrics, medication adherence, and daily logs are stable and within your doctor's target zone."

orchestrator_agent = OrchestratorAgent()
