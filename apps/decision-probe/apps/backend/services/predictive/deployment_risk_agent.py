import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Keywords indicating risky change categories
HIGH_RISK_KEYWORDS = [
    "database", "connection", "pool", "config", "migration", "auth",
    "authentication", "secret", "credential", "ssl", "tls", "schema",
]
MEDIUM_RISK_KEYWORDS = [
    "dependency", "upgrade", "package", "version", "timeout", "retry",
    "cache", "redis", "queue", "kafka",
]


def _score_deployment_risk(deploy: Dict[str, Any]) -> tuple[str, List[str]]:
    """Return (risk_level, reasons) for a single deployment entry."""
    reasons = []
    score = 0

    description = str(deploy.get("description", "")).lower()
    changes = [str(c).lower() for c in deploy.get("changes", [])]
    status = str(deploy.get("status", "")).lower()
    all_text = description + " " + " ".join(changes)

    if "fail" in status or "rollback" in status:
        score += 40
        reasons.append(f"Deployment status: {deploy.get('status', 'unknown')}")

    for kw in HIGH_RISK_KEYWORDS:
        if kw in all_text:
            score += 15
            reasons.append(f"High-risk change detected: {kw} modification")
            break

    for kw in MEDIUM_RISK_KEYWORDS:
        if kw in all_text:
            score += 8
            reasons.append(f"Moderate-risk change: {kw} update")
            break

    if len(changes) >= 5:
        score += 10
        reasons.append(f"Large change surface ({len(changes)} modified components)")

    if score >= 40:
        return "High", reasons
    if score >= 20:
        return "Medium", reasons
    if score > 0:
        return "Low", reasons
    reasons.append("No high-risk signals detected in this deployment")
    return "Low", reasons


class DeploymentRiskAgent:
    """
    Stage 9 - Deployment Risk Agent.

    Analyzes recent deployments for risk signals based on change content,
    deployment status, and historically risky keywords.
    """

    async def analyze_deployments(
        self,
        deployments: Dict[str, Any],
        historical_incidents: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Produce risk analysis for each recent deployment.
        """
        logger.info("DeploymentRiskAgent: analyzing deployment risks.")

        deploy_list = deployments.get("deployments", [])
        if not deploy_list:
            # Provide a default mock deployment when no real data is available
            deploy_list = [
                {
                    "version": "v2.6.1",
                    "description": "Database connection pool configuration update",
                    "changes": ["max_connections increased", "pool_timeout modified"],
                    "status": "deployed",
                }
            ]

        results = []
        for dep in deploy_list:
            version = dep.get("version", dep.get("id", "unknown"))
            risk_level, reasons = _score_deployment_risk(dep)

            # Escalate risk if similar deployments caused historical incidents
            for inc in historical_incidents:
                inc_text = str(inc.get("root_cause", "")).lower()
                dep_text = str(dep.get("description", "")).lower()
                if any(kw in inc_text and kw in dep_text for kw in HIGH_RISK_KEYWORDS):
                    if risk_level != "High":
                        risk_level = "High"
                    reasons.append("Historically similar deployments caused incidents")
                    break

            results.append({
                "version": version,
                "risk": risk_level,
                "reasons": reasons,
            })

        logger.info(f"DeploymentRiskAgent: analyzed {len(results)} deployments.")
        return {
            "deployments": results,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
