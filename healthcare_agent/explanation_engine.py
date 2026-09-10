from typing import Dict, Any, List

class ExplanationEngine:
    """
    Synthesizes clinical signals into two transparent, actionable pillars:
    1. WHAT CHANGED? (Empirical deltas in vitals, labs, symptoms, adherence)
    2. WHY IT MATTERS? (Pathophysiological mechanisms, risk trajectories, clinical impacts)
    """

    def generate_explanation(self, patient_360: Dict[str, Any], vitals_analysis: Dict[str, Any], monitoring_status: Dict[str, Any], lab_anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        what_changed = []
        why_it_matters = []

        # 1. Evaluate Vitals Deltas
        sbp = vitals_analysis.get("systolic_bp", {})
        if sbp.get("current") is not None and sbp.get("baseline") is not None:
            curr_sbp = sbp["current"]
            base_sbp = sbp["baseline"]
            delta = sbp.get("delta", 0)
            if curr_sbp >= 180:
                what_changed.append(f"Systolic Blood Pressure experienced an acute surge to {curr_sbp} mmHg (+{delta} mmHg vs baseline).")
                why_it_matters.append("Hypertensive crisis threshold reached; severe risk of acute end-organ damage (ischemic stroke, hypertensive encephalopathy, or acute heart strain).")
            elif delta >= 15:
                what_changed.append(f"Systolic Blood Pressure climbed by +{delta} mmHg over recent monitoring window (currently {curr_sbp} mmHg).")
                why_it_matters.append("Sustained blood pressure elevation increases left ventricular afterload and accelerates vascular remodeling.")

        spo2 = vitals_analysis.get("spo2", {})
        if spo2.get("current") is not None:
            curr_spo2 = spo2["current"]
            if curr_spo2 <= 90:
                what_changed.append(f"Oxygen Saturation (SpO2) dropped critically to {curr_spo2}% (Normal > 95%).")
                why_it_matters.append("Hypoxemia signals impaired alveolar-capillary gas exchange, acute pulmonary edema, or severe airway obstruction requiring supplemental oxygen.")

        glucose = vitals_analysis.get("blood_glucose", {})
        if glucose.get("current") is not None:
            curr_g = glucose["current"]
            if curr_g >= 200:
                what_changed.append(f"Blood Glucose level elevated to {curr_g} mg/dL.")
                why_it_matters.append("Uncontrolled hyperglycemia increases serum osmolality, exacerbates peripheral neuropathy, and accelerates microvascular complications.")

        # 2. Evaluate Medication Adherence Deltas
        for med in monitoring_status.get("adherence_details", []):
            if med["adherence_rate"] < 80:
                what_changed.append(f"Adherence for {med['medication_name']} ({med['dosage']}) dropped to {med['adherence_rate']}% with {med['missed_doses']} missed doses.")
                why_it_matters.append(f"Interrupted pharmacokinetics of {med['medication_name']} compromises therapeutic plasma concentration, triggering rebound symptoms.")

        # 3. Evaluate Lab Biomarkers
        for lab in lab_anomalies:
            what_changed.append(f"Abnormal {lab['biomarker']}: {lab['value']} {lab['unit']} (Ref: {lab['reference_range']}) flagged as {lab['status']}.")
            if "BNP" in lab["biomarker"].upper():
                why_it_matters.append("Markedly elevated cardiac wall stress indicator confirming myocardial strain or ventricular volume overload.")
            elif "CREATININE" in lab["biomarker"].upper() or "ALBUMIN" in lab["biomarker"].upper():
                why_it_matters.append("Impaired glomerular filtration and ongoing renal vascular strain.")
            elif "HBA1C" in lab["biomarker"].upper():
                why_it_matters.append("Sub-optimal 3-month glycemic control necessitating medication regimen adjustment.")

        # 4. Evaluate Symptoms
        recent_sym = monitoring_status.get("recent_symptom", {})
        if recent_sym and recent_sym.get("severity", 0) >= 6:
            what_changed.append(f"Patient reported high-severity symptom: '{recent_sym.get('symptom_name')}' (Severity {recent_sym.get('severity')}/10).")
            why_it_matters.append("Severe patient-reported discomfort correlates with active physiological instability.")

        # Fallback if baseline is stable
        if not what_changed:
            what_changed.append("Patient parameters, vitals, and adherence remain stable within expected clinical baselines.")
            why_it_matters.append("Current therapeutic regimen is effective; continue routine maintenance monitoring.")

        return {
            "what_changed": what_changed,
            "why_it_matters": why_it_matters
        }

explanation_engine = ExplanationEngine()
