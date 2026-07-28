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

class ResolutionTrackerAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.use_real_client = GENAI_AVAILABLE and bool(self.api_key) and self.api_key != "dummy"
        
        if self.use_real_client:
            logger.info("Resolution Tracker Agent initializing real GenAI Client.")
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("Resolution Tracker Agent running in OFFLINE/MOCK mode.")
            self.client = None

    async def evaluate_resolution(
        self,
        tasks: List[Dict[str, Any]],
        remediation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluates task lists and logs current resolution state, closed fixes, and remaining risks.
        """
        if not self.use_real_client:
            logger.info("Using offline mock resolution tracker agent.")
            return self._generate_mock_resolution(remediation)

        prompt = f"""You are the Resolution Tracker Agent inside Decision Probe.
Your responsibility is to analyze response task statuses and remediation logs to determine resolution state and risks.

Assigned Tasks: {json.dumps(tasks)}
Remediation Options: {json.dumps(remediation)}

CRITICAL RULES:
1. Classify state: "resolved" (all tasks done), "monitoring" (primary actions done, testing), "open" (tasks active).
2. Output MUST be a single raw JSON object matching the schema below (do not wrap in markdown codeblocks):

Expected JSON Output Schema:
{{
  "status": "resolved" or "monitoring" or "open",
  "completed_actions": [
    "Completed fix action item description"
  ],
  "remaining_risks": [
    "Identified remaining risk description"
  ]
}}
"""
        try:
            logger.info("Calling Gemini API to evaluate resolution progress.")
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
            logger.error(f"Failed to track resolution via Gemini: {e}. Falling back to mock resolution.")
            return self._generate_mock_resolution(remediation)

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()
        
        parsed = json.loads(raw_text)
        return {
            "status": parsed.get("status", "open"),
            "completed_actions": parsed.get("completed_actions", []),
            "remaining_risks": parsed.get("remaining_risks", [])
        }

    def _generate_mock_resolution(self, remediation: Dict[str, Any]) -> Dict[str, Any]:
        fixes = remediation.get("immediate_actions", ["Database connections pool limit increased"])
        return {
            "status": "monitoring",
            "completed_actions": [
                fixes[0] if fixes else "Database connection limits increased"
            ],
            "remaining_risks": [
                "Connection pooling might leak under sudden peak traffic spikes"
            ]
        }
