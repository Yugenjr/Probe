import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class PredictionAgent:
    """
    Stage 9 - Prediction Agent.

    Forecasts likely failures for affected services by correlating risk scores,
    anomalies, historical incident patterns, and deployment signals.
    Output includes confidence score and estimated time window.
    """

    async def forecast_failures(
        self,
        risk_scores: Dict[str, Any],
        anomalies: Dict[str, Any],
        historical_incidents: List[Dict[str, Any]],
        features: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Forecast likely failures for each at-risk service.
        """
        logger.info("PredictionAgent: forecasting failures.")

        services = risk_scores.get("services", [])
        anomaly_list = anomalies.get("anomalies", [])
        feat = features.get("features", {})
        predictions = []

        critical_anomalies = [a for a in anomaly_list if a.get("severity") in ("Critical", "High")]

        for svc in services:
            score = svc.get("risk_score", 0)
            if score < 30:
                continue  # Skip low-risk services

            svc_name = svc["service"]
            reasoning = list(svc.get("contributors", []))
            predicted_issue = "Service Degradation"
            confidence = 0.0
            time_window = "Next 48 Hours"

            # Determine primary predicted issue from anomalies
            db_anomaly = next((a for a in anomaly_list if "Database" in a.get("metric", "")), None)
            cpu_anomaly = next((a for a in anomaly_list if "CPU" in a.get("metric", "")), None)
            latency_anomaly = next((a for a in anomaly_list if "Latency" in a.get("metric", "")), None)
            error_anomaly = next((a for a in anomaly_list if "Error" in a.get("metric", "")), None)

            if db_anomaly:
                predicted_issue = "Database Connection Exhaustion"
                reasoning.append("Database connection anomaly detected above critical threshold")
            elif cpu_anomaly:
                predicted_issue = "CPU Resource Saturation"
                reasoning.append("CPU utilization trending toward saturation")
            elif latency_anomaly:
                predicted_issue = "Latency SLA Breach"
                reasoning.append("Response latency exceeds acceptable SLA thresholds")
            elif error_anomaly:
                predicted_issue = "Cascading Error Surge"
                reasoning.append("Error rate trending toward failure cascade")

            # Compute confidence from risk score + anomaly severity
            base_confidence = score / 100.0
            anomaly_boost = len(critical_anomalies) * 0.05
            inc_boost = min(len(historical_incidents) * 0.03, 0.12)
            confidence = round(min(base_confidence + anomaly_boost + inc_boost, 0.99), 2)

            # Estimate time window from score
            if score >= 81:
                time_window = "Next 6 Hours"
            elif score >= 61:
                time_window = "Next 24 Hours"
            elif score >= 31:
                time_window = "Next 48 Hours"

            if len(historical_incidents) >= 3:
                reasoning.append(f"High historical recurrence ({len(historical_incidents)} past incidents)")

            predictions.append({
                "service": svc_name,
                "predicted_issue": predicted_issue,
                "confidence": confidence,
                "estimated_time_window": time_window,
                "reasoning": reasoning[:5],  # cap to 5 reasons
            })

        logger.info(f"PredictionAgent: generated {len(predictions)} predictions.")
        return {
            "predictions": predictions,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
