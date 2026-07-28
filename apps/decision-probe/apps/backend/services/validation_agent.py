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

class ValidationAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.use_real_client = GENAI_AVAILABLE and bool(self.api_key) and self.api_key != "dummy"
        
        if self.use_real_client:
            logger.info("Validation Agent initializing real GenAI Client.")
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("Validation Agent running in OFFLINE/MOCK mode.")
            self.client = None

    async def validate_root_cause(
        self,
        root_cause: Dict[str, Any],
        timeline: Dict[str, Any],
        graph: Dict[str, Any],
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validates the selected root cause, maps assumptions, suggests verification steps,
        and identifies missing information.
        """
        rc_title = root_cause.get("title", "")
        
        # Check if root cause is insufficient evidence
        if rc_title == "Insufficient Evidence" or not chunks:
            return {
                "validation_plan": [
                    {
                        "action": "Upload system logs or event diagnostics",
                        "reason": "Provide baseline evidence context for reasoning pipeline"
                    }
                ],
                "missing_information": [
                    "Infrastructure metrics",
                    "Application deployment logs"
                ],
                "validation_summary": "Validation failed because the root cause decision contains insufficient evidence."
            }

        if not self.use_real_client:
            logger.info("Using offline mock validation agent.")
            return self._generate_mock_validation(root_cause)

        chunks_str = ""
        for idx, chk in enumerate(chunks):
            chunk_id = chk.get("id", f"chunk_{idx}")
            title = chk.get("title", "Unknown File")
            content = chk.get("snippet", chk.get("content", ""))
            chunks_str += f"--- START CHUNK ID: {chunk_id} (Source: {title}) ---\n{content}\n--- END CHUNK ---\n\n"

        prompt = f"""You are the Validation Agent inside Decision Probe.
Your responsibility is to validate the selected root cause, identify unsupported assumptions, list missing info, and suggest concrete validation steps.

Root Cause: {json.dumps(root_cause)}
Incident Timeline: {json.dumps(timeline)}
Evidence Graph: {json.dumps(graph)}

Retrieved Evidence Chunks:
{chunks_str}

CRITICAL RULES:
1. Verify if the supporting evidence is sufficient to justify the root cause.
2. Suggest concrete validation steps to prove or disprove the selected root cause.
3. List missing logs, config changes, metric charts, or trace details required.
4. Output MUST be a single raw JSON object matching the schema below (do not wrap in markdown codeblocks):

Expected JSON Output Schema:
{{
  "validation_plan": [
    {{
      "action": "Concrete verification command or diagnostic step",
      "reason": "Why this action is needed to validate the root cause"
    }}
  ],
  "missing_information": [
    "Metric name, log file, or environment setting that was not found but is needed"
  ],
  "validation_summary": "Comprehensive validation summary assessing the evidence sufficiency"
}}
"""
        try:
            logger.info("Calling Gemini API to validate root cause.")
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
            logger.error(f"Failed to validate via Gemini: {e}. Falling back to mock validation.")
            return self._generate_mock_validation(root_cause)

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()
        
        parsed = json.loads(raw_text)
        return {
            "validation_plan": parsed.get("validation_plan", []),
            "missing_information": parsed.get("missing_information", []),
            "validation_summary": parsed.get("validation_summary", "")
        }

    def _generate_mock_validation(self, root_cause: Dict[str, Any]) -> Dict[str, Any]:
        title_lower = root_cause.get("title", "").lower()
        
        if "pool" in title_lower or "postgres" in title_lower or "database" in title_lower:
            plan = [
                {
                    "action": "Check PostgreSQL max_connections configuration",
                    "reason": "Verify database connection limit constraints"
                },
                {
                    "action": "Analyze application connection pool metrics",
                    "reason": "Confirm connection exhaustion during incident"
                }
            ]
            missing = [
                "Database metrics",
                "Application request volume logs"
            ]
            summary = "The database connection limits are highly likely the root cause, but require checking PostgreSQL max_connections settings and pool usage charts to validate."
        elif "deploy" in title_lower or "config" in title_lower:
            plan = [
                {
                    "action": "Verify deployment environment variables",
                    "reason": "Ensure valid database credentials and parameters were supplied"
                },
                {
                    "action": "Inspect Kubernetes deployment manifest history",
                    "reason": "Identify config adjustments made preceding the failure"
                }
            ]
            missing = [
                "ConfigMaps and secrets version history",
                "Active deployment rollout state logs"
            ]
            summary = "The deployment config mismatch requires audit reviews of the environment settings and Kube configs rollouts."
        else:
            plan = [
                {
                    "action": "Collect application error stack traces",
                    "reason": "Isolate the root crash point of the service"
                }
            ]
            missing = [
                "Detailed application runtime debug metrics"
            ]
            summary = "General verification plan to locate standard logs and runtime trace information."

        return {
            "validation_plan": plan,
            "missing_information": missing,
            "validation_summary": summary
        }
