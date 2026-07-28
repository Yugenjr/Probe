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

class SimilarityAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.use_real_client = GENAI_AVAILABLE and bool(self.api_key) and self.api_key != "dummy"
        
        if self.use_real_client:
            logger.info("Knowledge Similarity Agent initializing real GenAI Client.")
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("Knowledge Similarity Agent running in OFFLINE/MOCK mode.")
            self.client = None

    async def compare_incidents(
        self,
        current_incident: Dict[str, Any],
        similar_incidents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Performs similarity compare mapping common patterns and differences.
        """
        if not self.use_real_client:
            logger.info("Using offline mock similarity comparison agent.")
            return self._generate_mock_comparison(current_incident)

        prompt = f"""You are the Similarity Agent inside Decision Probe.
Compare the current incident with historical incidents to extract patterns, difference deltas, and confidence adjustments.

Current Incident: {json.dumps(current_incident)}
Similar Incidents: {json.dumps(similar_incidents)}

CRITICAL RULES:
1. Identify overlaps in architecture, logs, and database metrics.
2. Output MUST be a single raw JSON object matching the schema below (do not wrap in markdown codeblocks):

Expected JSON Output Schema:
{{
  "common_patterns": [
    "Pattern description (e.g. Database saturation, network packet loss)"
  ],
  "differences": [
    "Delta description (e.g. Different deployment version, different API endpoint)"
  ],
  "confidence_boost": 0.15
}}
"""
        try:
            logger.info("Calling Gemini API to perform similarity comparison.")
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
            logger.error(f"Failed to compare incidents via Gemini: {e}. Falling back to mock comparison.")
            return self._generate_mock_comparison(current_incident)

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()
        
        parsed = json.loads(raw_text)
        return {
            "common_patterns": parsed.get("common_patterns", []),
            "differences": parsed.get("differences", []),
            "confidence_boost": parsed.get("confidence_boost", 0.0)
        }

    def _generate_mock_comparison(self, current_incident: Dict[str, Any]) -> Dict[str, Any]:
        title = current_incident.get("incident_title", "").lower()
        if "database" in title or "connection" in title:
            common = ["Database connection limits saturation"]
            diffs = ["Different deployed versions and config thresholds"]
            boost = 0.15
        else:
            common = ["High memory footprint and latency spikes"]
            diffs = ["Affected service endpoints vary slightly"]
            boost = 0.10
        return {
            "common_patterns": common,
            "differences": diffs,
            "confidence_boost": boost
        }
