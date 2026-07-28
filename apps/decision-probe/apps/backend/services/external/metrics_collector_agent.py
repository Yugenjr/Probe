import time
from typing import Dict, Any, List

class MetricsCollectorAgent:
    def __init__(self):
        pass

    async def fetch(self, service_name: str, time_range: str) -> List[Dict[str, Any]]:
        # Simulated metrics fetch (e.g. Prometheus)
        time_str = "2026-07-24T10:41:12Z"
        raw_metrics = [
            {"metric_name": "cpu_usage", "val": 85.0, "time": time_str},
            {"metric_name": "memory_usage", "val": 72.5, "time": time_str},
            {"metric_name": "db_connections", "val": 98.0, "time": time_str},
            {"metric_name": "latency", "val": 1500.0, "time": time_str},
            {"metric_name": "request_rate", "val": 450.0, "time": time_str}
        ]
        return raw_metrics

    def normalize(self, raw_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        normalized = []
        for m in raw_metrics:
            normalized.append({
                "name": m.get("metric_name", ""),
                "value": m.get("val", 0.0),
                "timestamp": m.get("time", "")
            })
        return {"metrics": normalized}

    def validate(self, normalized_data: Dict[str, Any]) -> bool:
        if "metrics" not in normalized_data:
            return False
        for m in normalized_data["metrics"]:
            if not all(k in m for k in ["name", "value", "timestamp"]):
                return False
        return True
