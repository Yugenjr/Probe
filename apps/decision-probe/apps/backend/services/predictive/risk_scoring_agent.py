import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Risk level thresholds
RISK_THRESHOLDS = {
    "Critical": 81,
    "High": 61,
    "Moderate": 31,
    "Low": 0,
}


def _classify_risk(score: int) -> str:
    if score >= RISK_THRESHOLDS["Critical"]:
        return "Critical"
    if score >= RISK_THRESHOLDS["High"]:
        return "High"
    if score >= RISK_THRESHOLDS["Moderate"]:
        return "Moderate"
    return "Low"


class RiskScoringAgent:
    """
    Stage 9 - Risk Scoring Agent.

    Computes a 0-100 risk score for every affected service by weighting
    extracted telemetry features and historical incident signal.

    Risk Levels:
        0-30  → Low
        31-60 → Moderate
        61-80 → High
        81-100 → Critical
    """

    async def score_services(
        self,
        features: Dict[str, Any],
        historical_incidents: List[Dict[str, Any]],
        graph: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Produce per-service risk scores from feature signals.
        """
        logger.info("RiskScoringAgent: computing service risk scores.")

        feat = features.get("features", {})
        cpu = feat.get("cpu_average", 0)
        db = feat.get("db_connections", 0)
        err = feat.get("error_rate", 0)
        latency = feat.get("latency_ms", 0)
        inc_freq = feat.get("incident_frequency", 0)
        failed_dep = feat.get("failed_deployments", 0)

        # Derive service names from evidence graph nodes
        nodes = graph.get("nodes", [])
        service_names = [n["name"] for n in nodes if n.get("type") in ("service", "api", "application")]
        if not service_names:
            service_names = ["payments-api"]

        services_out = []
        for svc in service_names:
            contributors = []
            score = 0

            if cpu > 80:
                score += 20
                contributors.append(f"CPU utilization elevated at {cpu:.0f}%")
            elif cpu > 60:
                score += 10
                contributors.append(f"CPU utilization moderate at {cpu:.0f}%")

            if db > 90:
                score += 30
                contributors.append(f"Database connections critical at {db:.0f}%")
            elif db > 70:
                score += 18
                contributors.append(f"Database connections elevated at {db:.0f}%")

            if err > 15:
                score += 20
                contributors.append(f"Error rate high at {err:.0f}%")
            elif err > 8:
                score += 10
                contributors.append(f"Error rate elevated at {err:.0f}%")

            if latency > 1000:
                score += 15
                contributors.append(f"Response latency critical at {latency:.0f}ms")
            elif latency > 600:
                score += 8
                contributors.append(f"Response latency elevated at {latency:.0f}ms")

            if inc_freq >= 3:
                score += 15
                contributors.append(f"High historical incident frequency ({inc_freq} incidents)")
            elif inc_freq >= 1:
                score += 7
                contributors.append(f"Prior incidents recorded ({inc_freq})")

            if failed_dep >= 2:
                score += 10
                contributors.append(f"Recent deployment failures ({failed_dep})")
            elif failed_dep == 1:
                score += 5
                contributors.append("One recent deployment failure")

            score = min(score, 100)
            if not contributors:
                contributors.append("No significant risk signals detected")

            services_out.append({
                "service": svc,
                "risk_score": score,
                "risk_level": _classify_risk(score),
                "contributors": contributors,
            })

        return {
            "services": services_out,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
