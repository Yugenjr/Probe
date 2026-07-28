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

class EvidenceGapAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.use_real_client = GENAI_AVAILABLE and bool(self.api_key) and self.api_key != "dummy"
        
        if self.use_real_client:
            logger.info("Evidence Gap Agent initializing real GenAI Client.")
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("Evidence Gap Agent running in OFFLINE/MOCK mode.")
            self.client = None

    async def analyze_gaps(
        self,
        root_cause: Dict[str, Any],
        validation: Dict[str, Any],
        critic_reviews: List[Dict[str, Any]],
        timeline: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyzes the root cause decision, weaknesses, and validation outputs to identify missing evidence.
        """
        rc = root_cause.get("root_cause", {})
        rc_title = rc.get("title", "")
        rc_confidence = rc.get("confidence", 0.0)

        # If confidence is high or insufficient evidence is final, don't continue
        if rc_confidence >= 0.85 or rc_title == "Insufficient Evidence":
            return {
                "evidence_gaps": [],
                "should_continue": False
            }

        if not self.use_real_client:
            logger.info("Using offline mock evidence gap agent.")
            return self._generate_mock_gaps(rc_title)

        prompt = f"""You are the Evidence Gap Agent inside Decision Probe.
Your responsibility is to analyze the root cause decision, critic weaknesses, validation summaries, and timeline data to output evidence gaps and decide if the loop should continue.

Root Cause: {json.dumps(root_cause)}
Validation: {json.dumps(validation)}
Critic Reviews: {json.dumps(critic_reviews)}
Timeline: {json.dumps(timeline)}

CRITICAL RULES:
1. Identify missing telemetry, logs, or settings that would fully prove the selected root cause.
2. Determine "should_continue": true if there are critical missing gaps and root cause confidence is low (< 0.85).
3. Output MUST be a single raw JSON object matching the schema below (do not wrap in markdown codeblocks):

Expected JSON Output Schema:
{{
  "evidence_gaps": [
    {{
      "gap": "Specific missing evidence details",
      "importance": "high" or "medium" or "low",
      "required_source": "Source system name (e.g., Kubernetes, Prometheus, Datadog)",
      "reason": "Why this gap is important to resolve the root cause"
    }}
  ],
  "should_continue": true or false
}}
"""
        try:
            logger.info("Calling Gemini API to analyze evidence gaps.")
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
            logger.error(f"Failed to analyze gaps via Gemini: {e}. Falling back to mock gap analysis.")
            return self._generate_mock_gaps(rc_title)

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()
        
        parsed = json.loads(raw_text)
        return {
            "evidence_gaps": parsed.get("evidence_gaps", []),
            "should_continue": parsed.get("should_continue", True)
        }

    def _generate_mock_gaps(self, title: str) -> Dict[str, Any]:
        title_lower = title.lower()
        
        if "pool" in title_lower or "postgres" in title_lower or "database" in title_lower:
            gaps = [
                {
                    "gap": "Database connection usage metrics",
                    "importance": "high",
                    "required_source": "PostgreSQL Monitoring",
                    "reason": "Required to confirm connection exhaustion hypothesis"
                }
            ]
        elif "deploy" in title_lower or "config" in title_lower:
            gaps = [
                {
                    "gap": "Deployment configuration settings variables",
                    "importance": "medium",
                    "required_source": "CI/CD Rollout System",
                    "reason": "Required to verify parameter values mismatches"
                }
            ]
        else:
            gaps = [
                {
                    "gap": "General application telemetry statistics",
                    "importance": "low",
                    "required_source": "Infrastructure Monitoring",
                    "reason": "Required to supplement initial investigation context"
                }
            ]

        return {
            "evidence_gaps": gaps,
            "should_continue": True
        }
