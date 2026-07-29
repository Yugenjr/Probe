import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class FeatureExtractionAgent:
    """
    Stage 9 - Feature Extraction Agent.

    Consumes raw telemetry inputs (timeline events, logs, metrics, deployments,
    historical incidents, knowledge recommendations) and produces a normalized
    feature dictionary used by downstream predictive agents.
    """

    async def extract_features(
        self,
        timeline: Dict[str, Any],
        logs: Dict[str, Any],
        metrics: Dict[str, Any],
        deployments: Dict[str, Any],
        historical_incidents: List[Dict[str, Any]],
        knowledge_recs: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Produce normalized predictive features from all available telemetry inputs.
        """
        logger.info("FeatureExtractionAgent: extracting features from telemetry inputs.")

        events = timeline.get("events", [])
        error_events = [e for e in events if "error" in e.get("severity", "").lower()
                        or "fail" in e.get("description", "").lower()]

        raw_metrics = metrics.get("metrics", [])
        cpu_vals = [m["value"] for m in raw_metrics if "cpu" in m.get("name", "").lower()]
        mem_vals = [m["value"] for m in raw_metrics if "mem" in m.get("name", "").lower()]
        db_conn_vals = [m["value"] for m in raw_metrics if "connection" in m.get("name", "").lower()
                        or "db_conn" in m.get("name", "").lower()]
        error_rate_vals = [m["value"] for m in raw_metrics if "error" in m.get("name", "").lower()]
        latency_vals = [m["value"] for m in raw_metrics if "latency" in m.get("name", "").lower()
                        or "response_time" in m.get("name", "").lower()]

        deploy_list = deployments.get("deployments", [])
        failed_deploys = [d for d in deploy_list if "fail" in d.get("status", "").lower()
                          or "rollback" in d.get("status", "").lower()]

        features = {
            "cpu_average": round(sum(cpu_vals) / len(cpu_vals), 1) if cpu_vals else 72.0,
            "memory_average": round(sum(mem_vals) / len(mem_vals), 1) if mem_vals else 65.0,
            "db_connections": round(sum(db_conn_vals) / len(db_conn_vals), 1) if db_conn_vals else 88.0,
            "error_rate": round(sum(error_rate_vals) / len(error_rate_vals), 1) if error_rate_vals else 12.0,
            "latency_ms": round(sum(latency_vals) / len(latency_vals), 1) if latency_vals else 850.0,
            "incident_frequency": len(historical_incidents),
            "deployment_count": len(deploy_list),
            "failed_deployments": len(failed_deploys),
            "timeline_error_events": len(error_events),
            "knowledge_rec_count": len(knowledge_recs),
        }

        logger.info(f"FeatureExtractionAgent: extracted {len(features)} features.")
        return {"features": features}
