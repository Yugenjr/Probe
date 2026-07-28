import time
from typing import Dict, Any, List

class LogCollectorAgent:
    def __init__(self):
        pass

    async def fetch(self, service_name: str, time_range: str, keywords: List[str] = None) -> List[Dict[str, Any]]:
        # Simulated log fetch from external systems (e.g. ElasticSearch/Loki)
        # Returns raw log lines
        time_str = "2026-07-24T10:41:12Z"
        raw_data = [
            {
                "time": time_str,
                "app": service_name,
                "severity": "ERROR",
                "msg": f"Connection pool exhausted. active_connections=98 max_connections=100"
            },
            {
                "time": time_str,
                "app": service_name,
                "severity": "WARN",
                "msg": "Slow query detected: SELECT * FROM payments WHERE status = 'pending' (duration=1500ms)"
            }
        ]
        return raw_data

    def normalize(self, raw_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        normalized = []
        for log in raw_logs:
            normalized.append({
                "timestamp": log.get("time", ""),
                "service": log.get("app", ""),
                "level": log.get("severity", ""),
                "message": log.get("msg", "")
            })
        return {"logs": normalized}

    def validate(self, normalized_data: Dict[str, Any]) -> bool:
        if "logs" not in normalized_data:
            return False
        for log in normalized_data["logs"]:
            if not all(k in log for k in ["timestamp", "service", "level", "message"]):
                return False
        return True
