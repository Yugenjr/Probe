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

class SeverityAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.use_real_client = GENAI_AVAILABLE and bool(self.api_key) and self.api_key != "dummy"
        
        if self.use_real_client:
            logger.info("Severity Agent initializing real GenAI Client.")
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("Severity Agent running in OFFLINE/MOCK mode.")
            self.client = None

    async def classify_severity(
        self,
        root_cause: Dict[str, Any],
        metrics: Dict[str, Any],
        error_volume: int = 120
    ) -> Dict[str, Any]:
        """
        Classifies incident severity (SEV1-SEV4) based on root cause, metrics, and user impact.
        """
        if not self.use_real_client:
            logger.info("Using offline mock severity agent.")
            return self._generate_mock_severity(root_cause, error_volume)

        prompt = f"""You are the Severity Agent inside Decision Probe.
Your responsibility is to classify the incident severity ("SEV1", "SEV2", "SEV3", "SEV4") and provide impact reasoning.

Root Cause: {json.dumps(root_cause)}
Metrics: {json.dumps(metrics)}
Error Volume: {error_volume}

CRITICAL RULES:
1. Assess the customer impact: SEV1 (critical outage), SEV2 (high impact), SEV3 (medium impact), SEV4 (low impact).
2. Output MUST be a single raw JSON object matching the schema below (do not wrap in markdown codeblocks):

Expected JSON Output Schema:
{{
  "severity": "SEV1" or "SEV2" or "SEV3" or "SEV4",
  "impact_summary": "Description of the customer impact",
  "reasoning": [
    "Fact-based explanation of the severity decision"
  ]
}}
"""
        try:
            logger.info("Calling Gemini API to classify incident severity.")
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
            logger.error(f"Failed to classify severity via Gemini: {e}. Falling back to mock classification.")
            return self._generate_mock_severity(root_cause, error_volume)

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()
        
        parsed = json.loads(raw_text)
        return {
            "severity": parsed.get("severity", "SEV3"),
            "impact_summary": parsed.get("impact_summary", ""),
            "reasoning": parsed.get("reasoning", [])
        }

    def _generate_mock_severity(self, root_cause: Dict[str, Any], error_volume: int) -> Dict[str, Any]:
        rc_title = root_cause.get("title", "").lower()
        
        if error_volume > 100 or "exhaust" in rc_title or "limit" in rc_title or "postgres" in rc_title:
            severity = "SEV2"
            summary = "Payment failures affecting checkout transactions"
            reasoning = [
                "High database connection error rate detected",
                "Customer payment transactions blocked due to pool exhaustion"
            ]
        else:
            severity = "SEV3"
            summary = "Minor performance latency degradation on secondary service routes"
            reasoning = [
                "Service latency slightly elevated but direct customer checkouts remain unaffected"
            ]

        return {
            "severity": severity,
            "impact_summary": summary,
            "reasoning": reasoning
        }
