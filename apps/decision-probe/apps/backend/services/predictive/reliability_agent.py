import logging
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ReliabilityAgent:
    """
    Stage 9 - Reliability Agent.

    Aggregates service-level risk scores into a platform-wide reliability index
    and health summary. Outputs overall reliability percentage, healthy/warning/
    critical service counts, and a human-readable summary.
    """

    async def evaluate_reliability(
        self,
        risk_scores: Dict[str, Any],
        anomalies: Dict[str, Any],
        predictions: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Compute platform-wide reliability from risk score distribution.
        """
        logger.info("ReliabilityAgent: evaluating platform reliability.")

        services = risk_scores.get("services", [])
        total = len(services)

        if total == 0:
            return {
                "overall_reliability": 100,
                "healthy_services": 0,
                "warning_services": 0,
                "critical_services": 0,
                "summary": "No services detected in the evidence graph.",
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

        healthy = sum(1 for s in services if s.get("risk_level") == "Low")
        warning = sum(1 for s in services if s.get("risk_level") in ("Moderate", "High"))
        critical = sum(1 for s in services if s.get("risk_level") == "Critical")

        # Compute weighted reliability score
        avg_risk = sum(s.get("risk_score", 0) for s in services) / total
        overall_reliability = max(0, round(100 - avg_risk))

        anomaly_count = len(anomalies.get("anomalies", []))
        prediction_count = len(predictions.get("predictions", []))

        # Generate summary
        if overall_reliability >= 90:
            health_label = "stable"
        elif overall_reliability >= 70:
            health_label = "degraded"
        else:
            health_label = "at risk"

        parts = [
            f"Overall platform health is {health_label} with {overall_reliability}% reliability.",
        ]
        if critical > 0:
            parts.append(f"{critical} service(s) are in critical state and require immediate attention.")
        if warning > 0:
            parts.append(f"{warning} service(s) show elevated risk signals.")
        if anomaly_count > 0:
            parts.append(f"{anomaly_count} active metric anomalies detected.")
        if prediction_count > 0:
            parts.append(f"{prediction_count} failure(s) forecasted within operating windows.")

        summary = " ".join(parts)

        return {
            "overall_reliability": overall_reliability,
            "healthy_services": healthy,
            "warning_services": warning,
            "critical_services": critical,
            "summary": summary,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
