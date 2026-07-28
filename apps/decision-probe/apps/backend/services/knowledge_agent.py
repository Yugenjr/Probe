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

class KnowledgeAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.use_real_client = GENAI_AVAILABLE and bool(self.api_key) and self.api_key != "dummy"
        
        if self.use_real_client:
            logger.info("Knowledge Agent initializing real GenAI Client.")
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("Knowledge Agent running in OFFLINE/MOCK mode.")
            self.client = None

    async def generate_knowledge(
        self,
        root_cause: Dict[str, Any],
        remediation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Builds reusable incident post-mortem knowledge bases.
        """
        rc = root_cause.get("root_cause", {})
        rc_title = rc.get("title", "Database Exhaustion")
        rc_desc = rc.get("description", "Database pools saturated.")
        
        fixes = remediation.get("permanent_fixes", ["Implement adaptive pooling"])
        prev = remediation.get("prevention_steps", ["Add database alerts"])

        if not self.use_real_client:
            logger.info("Using offline mock knowledge agent.")
            return self._generate_mock_knowledge(rc_title, fixes, prev)

        prompt = f"""You are the Knowledge Agent inside Decision Probe.
Your responsibility is to summarize the incident post-mortem into concise reusable knowledge elements.

Root Cause: {rc_title} ({rc_desc})
Permanent Fixes: {json.dumps(fixes)}
Prevention Steps: {json.dumps(prev)}

CRITICAL RULES:
1. Summarize concise problem, solution, and prevention actions.
2. Output MUST be a single raw JSON object matching the schema below (do not wrap in markdown codeblocks):

Expected JSON Output Schema:
{{
  "problem": "One-sentence description of the problem",
  "solution": "One-sentence description of the engineering solution",
  "prevention": "One-sentence description of the alerting/prevention safeguard"
}}
"""
        try:
            logger.info("Calling Gemini API to synthesize incident knowledge.")
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
            logger.error(f"Failed to synthesize knowledge via Gemini: {e}. Falling back to mock knowledge.")
            return self._generate_mock_knowledge(rc_title, fixes, prev)

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()
        
        parsed = json.loads(raw_text)
        return {
            "problem": parsed.get("problem", ""),
            "solution": parsed.get("solution", ""),
            "prevention": parsed.get("prevention", "")
        }

    def _generate_mock_knowledge(self, title: str, fixes: List[str], prev: List[str]) -> Dict[str, Any]:
        return {
            "problem": "Database connection exhaustion causing payment service failures.",
            "solution": fixes[0] if fixes else "Adaptive connection pooling",
            "prevention": prev[0] if prev else "Added database saturation alerts"
        }
