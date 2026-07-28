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

class CommunicationAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.use_real_client = GENAI_AVAILABLE and bool(self.api_key) and self.api_key != "dummy"
        
        if self.use_real_client:
            logger.info("Communication Agent initializing real GenAI Client.")
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("Communication Agent running in OFFLINE/MOCK mode.")
            self.client = None

    async def generate_updates(
        self,
        incident_overview: Dict[str, Any],
        severity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Formulates status updates for Slack, Email, and status pages.
        """
        title = incident_overview.get("incident_title", "Database Outage")
        sev = severity.get("severity", "SEV2")
        impact = severity.get("impact_summary", "Service errors detected.")

        if not self.use_real_client:
            logger.info("Using offline mock communication agent.")
            return self._generate_mock_updates(title, sev, impact)

        prompt = f"""You are the Communication Agent inside Decision Probe.
Your responsibility is to format Slack notifications, status page updates, and SRE email communications.

Incident: {title}
Severity Level: {sev}
Impact Summary: {impact}

CRITICAL RULES:
1. Compose brief, clear messages for each channel.
2. Output MUST be a single raw JSON object matching the schema below (do not wrap in markdown codeblocks):

Expected JSON Output Schema:
{{
  "updates": [
    {{
      "channel": "slack" or "email" or "status_page",
      "message": "Notification broadcast update message string details"
    }}
  ]
}}
"""
        try:
            logger.info("Calling Gemini API to compose channel communications.")
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
            return self._parse_json(raw_text)
        except Exception as e:
            logger.error(f"Failed to generate updates via Gemini: {e}. Falling back to mock updates.")
            return self._generate_mock_updates(title, sev, impact)

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()
        
        parsed = json.loads(raw_text)
        return {
            "updates": parsed.get("updates", [])
        }

    def _generate_mock_updates(self, title: str, sev: str, impact: str) -> Dict[str, Any]:
        slack_msg = f"[*Incident Alert: {title}*] severity={sev} status=investigating. Impact: {impact}. SRE team is actively analyzing logs."
        email_msg = f"Dear Team,\nWe are currently investigating an incident: {title} ({sev}).\nImpact Details: {impact}.\nUpdates will follow."
        status_page_msg = f"Investigating elevated payment failures caused by database connection saturation."
        
        return {
            "updates": [
                {"channel": "slack", "message": slack_msg},
                {"channel": "email", "message": email_msg},
                {"channel": "status_page", "message": status_page_msg}
            ]
        }
        
# For backwards compatibility with the singular communication payload format in the prompt
# Example channel = slack, message = Investigate payment failures...
class CommunicationResponseWrapper:
    pass
