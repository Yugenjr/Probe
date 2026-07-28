import logging
from typing import List, Dict, Any
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class TimelineBuilder:
    @staticmethod
    def normalize_timestamp(ts_str: str) -> str:
        """
        Normalizes a timestamp string to standard ISO-8601 UTC format (YYYY-MM-DDTHH:MM:SSZ).
        Falls back to a default UTC string if parsing fails.
        """
        if not ts_str:
            return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        ts_str = ts_str.strip()
        
        # Replace space with T between date and time
        ts_str = ts_str.replace(" ", "T")
        
        # Strip trailing timezone offsets like +00:00 or similar
        # E.g., 2026-07-24T10:41:12+00:00 -> 2026-07-24T10:41:12Z
        ts_str = re.sub(r"\+\d{2}:\d{2}$", "Z", ts_str)
        ts_str = re.sub(r"\-\d{2}:\d{2}$", "Z", ts_str)

        # Remove milliseconds if present (e.g. 2026-07-24T10:41:12.123Z -> 2026-07-24T10:41:12Z)
        ts_str = re.sub(r"\.\d+(Z?)$", r"\1", ts_str)

        # Ensure it ends with Z
        if not ts_str.endswith("Z") and "T" in ts_str:
            ts_str += "Z"

        # Validate by parsing (optional validation check)
        try:
            # Check format match YYYY-MM-DDTHH:MM:SSZ
            datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%SZ")
            return ts_str
        except ValueError:
            # Return parsed datetime string if it matches other formats, otherwise fallback
            try:
                dt = datetime.fromisoformat(ts_str.replace("Z", ""))
                return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                logger.warning(f"Could not parse timestamp: {ts_str}. Defaulting.")
                return ts_str

    @staticmethod
    def build_timeline(events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Normalizes timestamps, merges duplicates, and sorts events chronologically.
        """
        if not events:
            return {"events": []}

        normalized_events = []
        for event in events:
            ts = TimelineBuilder.normalize_timestamp(event.get("timestamp", ""))
            normalized_events.append({
                "timestamp": ts,
                "type": event.get("type", "info").lower(),
                "service": event.get("service", "unknown").lower(),
                "description": event.get("description", "").strip(),
                "source_chunk": event.get("source_chunk", "unknown")
            })

        # Merge duplicates
        # We group by key: (timestamp, service, description)
        merged_map = {}
        for ev in normalized_events:
            key = (ev["timestamp"], ev["service"], ev["description"])
            if key not in merged_map:
                merged_map[key] = ev
            else:
                # Merge source chunks references uniquely
                existing_chunks = [c.strip() for c in merged_map[key]["source_chunk"].split(",") if c.strip()]
                new_chunk = ev["source_chunk"].strip()
                if new_chunk and new_chunk not in existing_chunks:
                    existing_chunks.append(new_chunk)
                merged_map[key]["source_chunk"] = ", ".join(sorted(existing_chunks))

        merged_events = list(merged_map.values())

        # Sort chronologically (ascending order)
        # Because we normalized timestamps to YYYY-MM-DDTHH:MM:SSZ, string sorting works perfectly!
        merged_events.sort(key=lambda x: (x["timestamp"], x["service"]))

        return {"events": merged_events}
