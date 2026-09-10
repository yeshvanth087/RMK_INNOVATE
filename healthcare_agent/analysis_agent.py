import numpy as np
from typing import Dict, Any, List

class ClinicalAnalysisAgent:
    """
    Analyzes patient vitals time-series, lab biomarkers, and monitoring alerts.
    Computes statistical deltas, trend regressions, and anomalies.
    """
    
    def analyze_vitals_trends(self, vitals: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not vitals:
            return {"status": "NO_DATA", "metrics": {}}

        # Vitals are sorted chronological ASC
        systolic_vals = [float(v["systolic_bp"]) for v in vitals if v.get("systolic_bp") is not None]
        diastolic_vals = [float(v["diastolic_bp"]) for v in vitals if v.get("diastolic_bp") is not None]
        spo2_vals = [float(v["spo2"]) for v in vitals if v.get("spo2") is not None]
        hr_vals = [float(v["heart_rate"]) for v in vitals if v.get("heart_rate") is not None]
        glucose_vals = [float(v["blood_glucose_mg_dl"]) for v in vitals if v.get("blood_glucose_mg_dl") is not None]

        latest = vitals[-1]
        baseline = vitals[0]

        is_spiking = False
        if len(systolic_vals) >= 2:
            if systolic_vals[-1] >= 170 or (systolic_vals[-1] - systolic_vals[0]) >= 15 or (systolic_vals[-1] - systolic_vals[-2]) >= 5:
                is_spiking = True

        analysis = {
            "total_recordings": len(vitals),
            "latest_reading": latest,
            "systolic_bp": {
                "current": latest.get("systolic_bp"),
                "baseline": baseline.get("systolic_bp"),
                "mean": round(float(np.mean(systolic_vals)), 1) if systolic_vals else None,
                "delta": round(float(systolic_vals[-1] - systolic_vals[0]), 1) if len(systolic_vals) >= 2 else 0,
                "trend": "SPIKING" if is_spiking else "STABLE"
            },
            "spo2": {
                "current": latest.get("spo2"),
                "mean": round(float(np.mean(spo2_vals)), 1) if spo2_vals else None,
                "min": min(spo2_vals) if spo2_vals else None,
                "is_hypoxic": latest.get("spo2", 100) <= 90
            },
            "heart_rate": {
                "current": latest.get("heart_rate"),
                "mean": round(float(np.mean(hr_vals)), 1) if hr_vals else None,
                "is_tachycardic": latest.get("heart_rate", 70) >= 100
            },
            "blood_glucose": {
                "current": latest.get("blood_glucose_mg_dl"),
                "mean": round(float(np.mean(glucose_vals)), 1) if glucose_vals else None,
                "is_hyperglycemic": latest.get("blood_glucose_mg_dl", 100) >= 180
            }
        }
        return analysis

    def analyze_lab_anomalies(self, labs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        anomalies = []
        for lab in labs:
            status = lab.get("status", "").upper()
            if "HIGH" in status or "ELEVATED" in status or "CRITICAL" in status or "ABNORMAL" in status:
                anomalies.append({
                    "test_name": lab["test_name"],
                    "biomarker": lab["biomarker"],
                    "value": lab["result_value"],
                    "unit": lab["unit"],
                    "reference_range": lab["reference_range"],
                    "status": lab["status"],
                    "test_date": lab["test_date"]
                })
        return anomalies

analysis_agent = ClinicalAnalysisAgent()
