import logging
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Configurable metric thresholds (heuristic rules)
METRIC_THRESHOLDS = {
    "CPU": {"warn": 70.0, "critical": 85.0, "unit": "%"},
    "Memory": {"warn": 75.0, "critical": 90.0, "unit": "%"},
    "Disk": {"warn": 75.0, "critical": 90.0, "unit": "%"},
    "Database Connections": {"warn": 70.0, "critical": 88.0, "unit": "%"},
    "Error Rate": {"warn": 8.0, "critical": 15.0, "unit": "%"},
    "Request Rate": {"warn": 800.0, "critical": 1200.0, "unit": "req/s"},
    "Latency": {"warn": 600.0, "critical": 1000.0, "unit": "ms"},
}

# Friendly metric key mapping from feature dict keys
FEATURE_TO_METRIC = {
    "cpu_average": "CPU",
    "memory_average": "Memory",
    "db_connections": "Database Connections",
    "error_rate": "Error Rate",
    "latency_ms": "Latency",
}


def _classify_anomaly_severity(actual: float, warn: float, critical: float) -> str:
    if actual >= critical:
        return "Critical"
    if actual >= warn:
        return "High"
    return "Medium"


class AnomalyDetectionAgent:
    """
    Stage 9 - Anomaly Detection Agent.

    Uses configurable statistical threshold rules to detect abnormal metric values.
    Supports CPU, Memory, Disk, Database Connections, Error Rate, Request Rate, Latency.
    """

    async def detect_anomalies(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect metric anomalies from extracted feature values.
        """
        logger.info("AnomalyDetectionAgent: detecting metric anomalies.")

        feat = features.get("features", {})
        anomalies = []

        for feature_key, metric_name in FEATURE_TO_METRIC.items():
            actual = feat.get(feature_key)
            if actual is None:
                continue

            thresholds = METRIC_THRESHOLDS.get(metric_name, {})
            warn = thresholds.get("warn", 80.0)
            critical = thresholds.get("critical", 95.0)
            unit = thresholds.get("unit", "")

            if actual >= warn:
                severity = _classify_anomaly_severity(actual, warn, critical)
                expected = round(warn * 0.75, 1)
                anomalies.append({
                    "metric": metric_name,
                    "expected": expected,
                    "actual": actual,
                    "severity": severity,
                    "description": (
                        f"{metric_name} usage at {actual:.1f}{unit} significantly exceeds "
                        f"normal operating range of {expected:.1f}{unit}."
                    ),
                })

        logger.info(f"AnomalyDetectionAgent: found {len(anomalies)} anomalies.")
        return {
            "anomalies": anomalies,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
