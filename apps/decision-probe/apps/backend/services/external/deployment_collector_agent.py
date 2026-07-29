import subprocess
from datetime import datetime, timezone
from typing import Dict, Any, List

class DeploymentCollectorAgent:
    def __init__(self):
        pass

    async def fetch(self, time_range: str) -> List[Dict[str, Any]]:
        # Fetch real local deployment events by checking the latest git tag or commit
        try:
            output = subprocess.check_output(
                ["git", "log", "-n", "1", "--pretty=format:%H|%an|%s|%cd", "--date=iso-strict"],
                text=True,
                encoding="utf-8"
            )
            raw_events = []
            if output:
                parts = output.strip().split("|", 3)
                if len(parts) >= 4:
                    raw_events.append({
                        "svc": "local-backend",
                        "tag": parts[0][:7],
                        "ts": parts[3],
                        "user": parts[1],
                        "desc": f"Latest update: {parts[2]}"
                    })
            return raw_events
        except Exception as e:
            print(f"Error fetching deployment changes: {e}")
            return []

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
