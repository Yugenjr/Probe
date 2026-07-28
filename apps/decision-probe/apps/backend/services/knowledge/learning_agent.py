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

class LearningAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.use_real_client = GENAI_AVAILABLE and bool(self.api_key) and self.api_key != "dummy"
        
        if self.use_real_client:
            logger.info("Knowledge Learning Agent initializing real GenAI Client.")
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("Knowledge Learning Agent running in OFFLINE/MOCK mode.")
            self.client = None

    async def generate_recommendations(
        self,
        current_incident: Dict[str, Any],
        similar_incidents: List[Dict[str, Any]],
        resolution_history: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Formulates action recommendations to improve future diagnostics.
        """
        if not self.use_real_client:
            logger.info("Using offline mock learning agent.")
            return self._generate_mock_recommendations(current_incident)

        prompt = f"""You are the Learning Agent inside Decision Probe.
Your responsibility is to analyze past similar incidents and the current resolution trace to formulate investigation/prevention recommendations.

Current Incident: {json.dumps(current_incident)}
Similar Incidents: {json.dumps(similar_incidents)}
Resolution History: {json.dumps(resolution_history)}

CRITICAL RULES:
1. Provide highly practical advice for SRE and developer teams.
2. Output MUST be a single raw JSON object matching the schema below (do not wrap in markdown codeblocks):

Expected JSON Output Schema:
{{
  "recommendations": [
    {{
      "type": "investigation" or "prevention",
      "suggestion": "Practical diagnostic suggestion detail"
    }}
  ]
}}
"""
        try:
            logger.info("Calling Gemini API to generate learning recommendations.")
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
            logger.error(f"Failed to generate recommendations via Gemini: {e}. Falling back to mock recommendations.")
            return self._generate_mock_recommendations(current_incident)

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()
        
        parsed = json.loads(raw_text)
        return {
            "recommendations": parsed.get("recommendations", [])
        }

    def _generate_mock_recommendations(self, current_incident: Dict[str, Any]) -> Dict[str, Any]:
        title = current_incident.get("incident_title", "").lower()
        if "database" in title or "connection" in title:
            return {
                "recommendations": [
                    {
                        "type": "investigation",
                        "suggestion": "Check database connection pool metrics first during query surges."
                    },
                    {
                        "type": "prevention",
                        "suggestion": "Enable database saturation alarms when connection rates exceed 85%."
                    }
                ]
            }
        else:
            return {
                "recommendations": [
                    {
                        "type": "investigation",
                        "suggestion": "Trace SRE logs for memory growth metrics on high-throughput services."
                    },
                    {
                        "type": "prevention",
                        "suggestion": "Set memory limit caps and automated process-recycle cron jobs."
                    }
                ]
            }
        
# For backwards compatibility with prompt singular wrapper naming
class LearningResponseWrapper:
    pass
