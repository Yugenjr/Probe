import os
import json
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Try importing google-genai
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

class IncidentCommanderAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.use_real_client = GENAI_AVAILABLE and bool(self.api_key) and self.api_key != "dummy"
        
        if self.use_real_client:
            logger.info("Incident Commander Agent initializing real GenAI Client.")
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("Incident Commander Agent running in OFFLINE/MOCK mode.")
            self.client = None

    async def generate_overview(
        self,
        root_cause: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Creates an incident command overview title, summary, affected services list, and status.
        """
        rc = root_cause.get("root_cause", {})
        rc_title = rc.get("title", "Unknown Database Failure")
        rc_desc = rc.get("description", "A database failure occurred.")
        rc_conf = rc.get("confidence", 0.0)

        if not self.use_real_client:
            logger.info("Using offline mock incident commander agent.")
            return self._generate_mock_overview(rc_title, rc_desc, rc_conf)

        prompt = f"""You are the Incident Commander Agent inside Decision Probe.
Your responsibility is to synthesize a high-level incident response overview based on the selected root cause.

Root Cause Title: {rc_title}
Root Cause Description: {rc_desc}
Root Cause Confidence: {rc_conf}

CRITICAL RULES:
1. Generate a descriptive incident title and executive summary.
2. Output MUST be a single raw JSON object matching the schema below (do not wrap in markdown codeblocks):

Expected JSON Output Schema:
{{
  "incident_title": "Descriptive incident title",
  "summary": "High-level summary of the ongoing incident",
  "affected_services": [
    "service-name"
  ],
  "root_cause": "Brief summary of root cause",
  "confidence": {rc_conf},
  "current_status": "investigating"
}}
"""
        try:
            logger.info("Calling Gemini API to synthesize incident overview.")
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0
                )
            )
            raw_text = response.text
            return self._parse_json(raw_text, rc_conf)
        except Exception as e:
            logger.error(f"Failed to generate overview via Gemini: {e}. Falling back to mock overview.")
            return self._generate_mock_overview(rc_title, rc_desc, rc_conf)

    def _parse_json(self, raw_text: str, default_conf: float) -> Dict[str, Any]:
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()
        
        parsed = json.loads(raw_text)
        return {
            "incident_title": parsed.get("incident_title", ""),
            "summary": parsed.get("summary", ""),
            "affected_services": parsed.get("affected_services", []),
            "root_cause": parsed.get("root_cause", ""),
            "confidence": parsed.get("confidence", default_conf),
            "current_status": parsed.get("current_status", "investigating")
        }

    def _generate_mock_overview(self, title: str, desc: str, confidence: float) -> Dict[str, Any]:
        return {
            "incident_title": "Payment Database Connection Failure",
            "summary": "Payment API unable to acquire database connections, causing customer transaction bottlenecks.",
            "affected_services": ["payments-api"],
            "root_cause": title,
            "confidence": confidence,
            "current_status": "investigating"
        }
