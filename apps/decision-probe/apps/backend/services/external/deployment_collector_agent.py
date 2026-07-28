import time
from typing import Dict, Any, List

class DeploymentCollectorAgent:
    def __init__(self):
        pass

    async def fetch(self, time_range: str) -> List[Dict[str, Any]]:
        # Simulated deployment events fetch (e.g. ArgoCD/Jenkins rollout events)
        time_str = "2026-07-24T10:40:00Z"
        raw_events = [
            {
                "svc": "payments",
                "tag": "v1.1.0",
                "ts": time_str,
                "user": "alex.engineer@company.com",
                "desc": "Release tag v1.1.0 including connection pooling reconfiguration update"
            }
        ]
        return raw_events

    def normalize(self, raw_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        normalized = []
        for ev in raw_events:
            normalized.append({
                "service": ev.get("svc", ""),
                "version": ev.get("tag", ""),
                "changed_at": ev.get("ts", ""),
                "author": ev.get("user", ""),
                "summary": ev.get("desc", "")
            })
        return {"changes": normalized}

    def validate(self, normalized_data: Dict[str, Any]) -> bool:
        if "changes" not in normalized_data:
            return False
        for change in normalized_data["changes"]:
            if not all(k in change for k in ["service", "version", "changed_at", "author", "summary"]):
                return False
        return True
