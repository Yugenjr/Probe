import time
import psutil
from datetime import datetime, timezone
from typing import Dict, Any, List

class MetricsCollectorAgent:
    def __init__(self):
        pass

    async def fetch(self, service_name: str, time_range: str) -> List[Dict[str, Any]]:
        # Fetch real system metrics using psutil
        time_str = datetime.now(timezone.utc).isoformat()
        
        cpu_percent = psutil.cpu_percent(interval=0.1)
        mem_info = psutil.virtual_memory()
        mem_percent = mem_info.percent
        
        # We can simulate request_rate and latency based on real stats or keep them close to real values 
        # For db_connections, since we don't have direct access, we can fetch network connections count
        connections = len(psutil.net_connections())
        
        raw_metrics = [
            {"metric_name": "cpu_usage", "val": cpu_percent, "time": time_str},
            {"metric_name": "memory_usage", "val": mem_percent, "time": time_str},
            {"metric_name": "network_connections", "val": float(connections), "time": time_str},
            {"metric_name": "latency", "val": 45.0, "time": time_str},  # dummy fallback for latency
            {"metric_name": "request_rate", "val": 12.0, "time": time_str} # dummy fallback for requests
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
