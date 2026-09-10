import os
import pandas as pd
from typing import Dict, Any, List

class ClinicalSafetyEngine:
    """
    Deterministic Safety & Escalation Engine based on escalation_rules.csv.
    Guarantees clinical safety boundaries by evaluating quantitative thresholds
    before any AI advice is given to patients or doctors.
    """

    def __init__(self, data_dir: str = "data"):
        self.rules_path = os.path.join(data_dir, "safety", "escalation_rules.csv")
        self.rules = []
        self._load_rules()

    def _load_rules(self):
        if os.path.exists(self.rules_path):
            df = pd.read_csv(self.rules_path)
            self.rules = df[df["is_active"] == 1].to_dict(orient="records")
            print(f"Safety Engine loaded {len(self.rules)} active clinical escalation rules.")

    def evaluate(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates a metrics payload (e.g. latest vitals, pain score, adherence rate)
        against all active escalation rules.
        """
        triggered_alerts = []
        is_critical = False
        is_warning = False

        for rule in self.rules:
            metric_name = rule["metric_name"]
            threshold = float(rule["threshold_value"])
            operator = rule["operator"]
            severity = str(rule["severity_level"]).upper()

            if metric_name in metrics and metrics[metric_name] is not None:
                val = float(metrics[metric_name])
                is_breached = False

                if operator == ">=" and val >= threshold:
                    is_breached = True
                elif operator == "<=" and val <= threshold:
                    is_breached = True
                elif operator == ">" and val > threshold:
                    is_breached = True
                elif operator == "<" and val < threshold:
                    is_breached = True
                elif operator == "==" and val == threshold:
                    is_breached = True

                if is_breached:
                    if severity == "CRITICAL":
                        is_critical = True
                    elif severity == "WARNING":
                        is_warning = True

                    triggered_alerts.append({
                        "rule_id": rule["rule_id"],
                        "rule_name": rule["rule_name"],
                        "metric": metric_name,
                        "observed_value": val,
                        "threshold": threshold,
                        "operator": operator,
                        "severity": severity,
                        "action": rule["escalation_action"],
                        "rationale": rule["clinical_rationale"]
                    })

        status = "CONCERN" if (is_critical or is_warning) else "NORMAL"
        triage_level = "EMERGENCY_CRITICAL" if is_critical else ("PHYSICIAN_WARNING" if is_warning else "STABLE")

        return {
            "status": status,
            "triage_level": triage_level,
            "requires_doctor_review": is_critical or is_warning,
            "requires_immediate_emergency": is_critical,
            "total_alerts": len(triggered_alerts),
            "triggered_rules": triggered_alerts
        }

safety_engine = ClinicalSafetyEngine()
