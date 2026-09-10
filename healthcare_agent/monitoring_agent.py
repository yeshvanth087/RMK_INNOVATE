from typing import Dict, Any, List

class DailyMonitoringAgent:
    """
    Monitors daily check-ins, medication adherence, symptoms progression,
    and produces personalized daily precautions and companion guidance.
    """

    def evaluate_monitoring_status(self, patient_360: Dict[str, Any]) -> Dict[str, Any]:
        checkins = patient_360.get("daily_checkins", [])
        meds = patient_360.get("medications", [])
        symptoms = patient_360.get("symptoms", [])

        # 1. Adherence assessment
        adherence_summary = []
        overall_adherence_sum = 0
        for m in meds:
            rate = float(m.get("adherence_rate") or 100.0)
            overall_adherence_sum += rate
            adherence_summary.append({
                "medication_name": m["medication_name"],
                "dosage": m["dosage"],
                "frequency": m["frequency"],
                "adherence_rate": rate,
                "missed_doses": m.get("missed_doses", 0),
                "trend": m.get("adherence_trend", "STABLE"),
                "is_non_compliant": rate < 80.0
            })
        
        avg_adherence = round(overall_adherence_sum / len(meds), 1) if meds else 100.0

        # 2. Check-in trend (pain and fatigue)
        recent_checkin = checkins[0] if checkins else {}
        pain_score = recent_checkin.get("pain_score", 0)
        fatigue_level = recent_checkin.get("fatigue_level", "Low")
        sleep_hours = recent_checkin.get("sleep_hours", 7.0)

        # 3. Active Symptoms
        recent_symptom = symptoms[0] if symptoms else {}

        # 4. Proactive Precautions Generation
        precautions = self.generate_daily_precautions(patient_360["primary_condition"], avg_adherence, pain_score)

        return {
            "avg_adherence_rate": avg_adherence,
            "adherence_details": adherence_summary,
            "recent_checkin": recent_checkin,
            "recent_symptom": recent_symptom,
            "pain_score": pain_score,
            "sleep_hours": sleep_hours,
            "fatigue_level": fatigue_level,
            "daily_precautions": precautions
        }

    def generate_daily_precautions(self, condition: str, adherence: float, pain: int) -> List[str]:
        precautions = []
        c_lower = condition.lower()

        if "hypertens" in c_lower:
            precautions.append("🧂 Maintain strict dietary sodium restriction (< 2g/day). Avoid canned or processed foods.")
            precautions.append("⏱️ Log your morning blood pressure before having tea or breakfast.")
            precautions.append("🧘 Avoid sudden physical exertion; practice 10 minutes of paced deep breathing.")

        if "diabet" in c_lower:
            precautions.append("👣 Perform daily visual inspection of your feet and between toes using a hand mirror.")
            precautions.append("🥗 Ensure low-glycemic meals and avoid skipping regular meal timings.")
            precautions.append("💧 Drink at least 2.5L of water daily to maintain renal filtration.")

        if "asthma" in c_lower:
            precautions.append("🌬️ Always keep your rescue inhaler accessible; rinse mouth thoroughly after preventer inhaler.")
            precautions.append("😷 Avoid heavy dust exposure, cold air drafts, and strong incense or aerosol sprays.")

        if "heart failure" in c_lower or "kidney" in c_lower:
            precautions.append("⚖️ Weigh yourself first thing in the morning. Alert doctor if weight increases by > 1.5 kg.")
            precautions.append("🥛 Adhere strictly to your prescribed fluid limit (1.2L - 1.5L / day).")
            precautions.append("🛏️ Sleep with head slightly elevated on extra pillows if orthopnea occurs.")

        if adherence < 80:
            precautions.append("⚠️ Set phone reminders or pill-box alarms for evening medications to prevent missed doses.")

        if pain >= 6:
            precautions.append("⚠️ Elevated pain levels detected. Avoid strenuous activity and keep emergency doctor contact ready.")

        return precautions

monitoring_agent = DailyMonitoringAgent()
