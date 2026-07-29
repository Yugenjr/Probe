import os
from typing import Dict, Any, List

class LogCollectorAgent:
    def __init__(self):
        pass

    async def fetch(self, service_name: str, time_range: str, keywords: List[str] = None) -> List[Dict[str, Any]]:
        # Fetch real logs from backend.log
        log_file = "backend.log"
        raw_data = []
        if os.path.exists(log_file):
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    # Get the last 100 lines
                    lines = f.readlines()[-100:]
                    for line in lines:
                        if not line.strip():
                            continue
                        parts = line.split(" - ", 3)
                        if len(parts) >= 4:
                            raw_data.append({
                                "time": parts[0],
                                "app": parts[1] or service_name,
                                "severity": parts[2],
                                "msg": parts[3].strip()
                            })
                        else:
                            raw_data.append({
                                "time": "",
                                "app": service_name,
                                "severity": "INFO",
                                "msg": line.strip()
                            })
            except Exception as e:
                print(f"Error reading logs: {e}")
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
