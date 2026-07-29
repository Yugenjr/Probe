import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

PRIORITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


class PreventiveRecommendationAgent:
    """
    Stage 9 - Preventive Recommendation Agent.

    Synthesizes advisory recommendations from risk scores, anomalies,
    predictions, and deployment risks. All outputs are advisory only —
    no automatic production changes are triggered.
    """

    async def generate_recommendations(
        self,
        risk_scores: Dict[str, Any],
        anomalies: Dict[str, Any],
        predictions: Dict[str, Any],
        deployment_risk: Dict[str, Any],
        features: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate prioritized preventive recommendations.
        """
        logger.info("PreventiveRecommendationAgent: generating recommendations.")

        recs: List[Dict[str, Any]] = []
        feat = features.get("features", {})

        # Recommendations from anomalies
        for anomaly in anomalies.get("anomalies", []):
            metric = anomaly.get("metric", "")
            severity = anomaly.get("severity", "Medium")
            actual = anomaly.get("actual", 0)
            expected = anomaly.get("expected", 0)

            priority = "High" if severity in ("Critical", "High") else "Medium"

            if "Database" in metric:
                recs.append({
                    "priority": priority,
                    "action": (
                        f"Increase PostgreSQL connection pool capacity. "
                        f"Current connections at {actual:.0f}% vs expected {expected:.0f}%. "
                        "Review pool_size and max_overflow settings before peak traffic."
                    ),
                    "rationale": f"Database connection anomaly detected at {actual:.0f}%.",
                })
            elif "CPU" in metric:
                recs.append({
                    "priority": priority,
                    "action": (
                        f"Investigate CPU spike: consider horizontal scaling or profiling "
                        f"hot paths. Current CPU at {actual:.0f}%."
                    ),
                    "rationale": f"CPU usage above warning threshold ({actual:.0f}%).",
                })
            elif "Latency" in metric:
                recs.append({
                    "priority": priority,
                    "action": (
                        f"Delay non-critical deployments until response latency returns to baseline. "
                        f"Current latency: {actual:.0f}ms."
                    ),
                    "rationale": "Latency exceeds SLA thresholds.",
                })
            elif "Error" in metric:
                recs.append({
                    "priority": priority,
                    "action": (
                        f"Investigate error spike. Enable circuit breakers to limit failure "
                        f"propagation. Error rate currently at {actual:.0f}%."
                    ),
                    "rationale": "Error rate trending toward cascade failure.",
                })
            elif "Memory" in metric:
                recs.append({
                    "priority": "Medium",
                    "action": (
                        f"Review memory allocation and check for leaks. "
                        f"Memory usage at {actual:.0f}%."
                    ),
                    "rationale": "Memory utilization elevated.",
                })

        # Recommendations from deployment risks
        for dep in deployment_risk.get("deployments", []):
            if dep.get("risk") in ("High", "Critical"):
                recs.append({
                    "priority": "High",
                    "action": (
                        f"Defer deployment {dep.get('version', 'unknown')} until stability improves. "
                        "Reasons: " + "; ".join(dep.get("reasons", [])[:2]) + "."
                    ),
                    "rationale": f"Deployment flagged as {dep['risk']} risk.",
                })

        # Recommendations from failure predictions
        for pred in predictions.get("predictions", []):
            if pred.get("confidence", 0) >= 0.75:
                recs.append({
                    "priority": "High",
                    "action": (
                        f"Proactively address {pred.get('predicted_issue', 'predicted failure')} "
                        f"on {pred.get('service', 'affected service')} before "
                        f"{pred.get('estimated_time_window', 'predicted window')}."
                    ),
                    "rationale": f"Confidence: {pred.get('confidence', 0):.0%}.",
                })
            elif pred.get("confidence", 0) >= 0.50:
                recs.append({
                    "priority": "Medium",
                    "action": (
                        f"Monitor {pred.get('service', 'service')} closely for signs of "
                        f"{pred.get('predicted_issue', 'potential failure')} "
                        f"(predicted within {pred.get('estimated_time_window', 'the next window')})."
                    ),
                    "rationale": f"Moderate confidence prediction ({pred.get('confidence', 0):.0%}).",
                })

        # General capacity recommendations based on features
        inc_freq = feat.get("incident_frequency", 0)
        if inc_freq >= 3:
            recs.append({
                "priority": "Medium",
                "action": (
                    "Conduct capacity planning review. High incident frequency suggests "
                    "systemic resource constraints that require architectural review."
                ),
                "rationale": f"High incident frequency: {inc_freq} incidents recorded.",
            })

        if not recs:
            recs.append({
                "priority": "Low",
                "action": "Continue monitoring. No actionable risk signals detected at this time.",
                "rationale": "All metrics within normal operating ranges.",
            })

        # Sort by priority
        recs.sort(key=lambda r: PRIORITY_ORDER.get(r.get("priority", "Low"), 3))

        logger.info(f"PreventiveRecommendationAgent: generated {len(recs)} recommendations.")
        return {
            "recommendations": recs,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
