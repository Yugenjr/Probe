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

class RemediationAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.use_real_client = GENAI_AVAILABLE and bool(self.api_key) and self.api_key != "dummy"
        
        if self.use_real_client:
            logger.info("Remediation Agent initializing real GenAI Client.")
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("Remediation Agent running in OFFLINE/MOCK mode.")
            self.client = None

    async def generate_remediation(
        self,
        root_cause: Dict[str, Any],
        validation: Dict[str, Any],
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generates remediation actions divided into immediate, permanent, and prevention fixes.
        """
        rc_title = root_cause.get("title", "")
        
        # Check if root cause is insufficient evidence
        if rc_title == "Insufficient Evidence" or not chunks:
            return {
                "immediate_actions": ["No immediate action can be determined. Please upload more log files."],
                "permanent_fixes": ["No permanent fix can be determined due to lack of baseline evidence."],
                "prevention_steps": ["Establish unified logging pipelines to gather baseline metrics."],
                "summary": "Remediation plan could not be generated because root cause decision has insufficient evidence."
            }

        if not self.use_real_client:
            logger.info("Using offline mock remediation agent.")
            return self._generate_mock_remediation(root_cause)

        chunks_str = ""
        for idx, chk in enumerate(chunks):
            chunk_id = chk.get("id", f"chunk_{idx}")
            title = chk.get("title", "Unknown File")
            content = chk.get("snippet", chk.get("content", ""))
            chunks_str += f"--- START CHUNK ID: {chunk_id} (Source: {title}) ---\n{content}\n--- END CHUNK ---\n\n"

        prompt = f"""You are the Remediation Agent inside Decision Probe.
Your responsibility is to analyze the selected root cause and its validation plan to generate recovery and prevention plans.

Root Cause: {json.dumps(root_cause)}
Validation: {json.dumps(validation)}

Retrieved Evidence Chunks:
{chunks_str}

CRITICAL RULES:
1. Suggest concrete recovery plans.
2. Group suggestions into:
   - "immediate_actions": Temporary recovery and stabilization steps
   - "permanent_fixes": Engineering adjustments to permanently resolve the issue
   - "prevention_steps": Monitoring, alerting, and process safeguards
3. Output MUST be a single raw JSON object matching the schema below (do not wrap in markdown codeblocks):

Expected JSON Output Schema:
{{
  "immediate_actions": [
    "Immediate recovery action item"
  ],
  "permanent_fixes": [
    "Permanent fix action item"
  ],
  "prevention_steps": [
    "Safeguard or alert configuration item"
  ],
  "summary": "High-level summary of the remediation strategy"
}}
"""
        try:
            logger.info("Calling Gemini API to generate remediation actions.")
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
            logger.error(f"Failed to generate remediation via Gemini: {e}. Falling back to mock remediation.")
            return self._generate_mock_remediation(root_cause)

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()
        
        parsed = json.loads(raw_text)
        return {
            "immediate_actions": parsed.get("immediate_actions", []),
            "permanent_fixes": parsed.get("permanent_fixes", []),
            "prevention_steps": parsed.get("prevention_steps", []),
            "summary": parsed.get("summary", "")
        }

    def _generate_mock_remediation(self, root_cause: Dict[str, Any]) -> Dict[str, Any]:
        title_lower = root_cause.get("title", "").lower()
        
        if "pool" in title_lower or "postgres" in title_lower or "database" in title_lower:
            immediate = [
                "Increase database connection pool limit",
                "Restart application instances to release stuck connection handles"
            ]
            permanent = [
                "Implement adaptive connection pooling",
                "Scale database connections or add replica reader nodes"
            ]
            prevention = [
                "Add database saturation alerts",
                "Configure connection leak detection monitors"
            ]
            summary = "Database connection exhaustion can be recovered immediately by increasing pool limits, and permanently fixed by implementing adaptive pooling strategies and replicas."
        elif "deploy" in title_lower or "config" in title_lower:
            immediate = [
                "Rollback to the previous stable release",
                "Inject valid credentials to config environment"
            ]
            permanent = [
                "Automate configuration schema validation checks in CI/CD pipeline"
            ]
            prevention = [
                "Add rollout check gate alerts for config modifications"
            ]
            summary = "Rollback the bad deployment immediately and automate configuration checks in release pipelines."
        else:
            immediate = [
                "Restart affected service process"
            ]
            permanent = [
                "Analyze memory leaks and patch core services code"
            ]
            prevention = [
                "Setup memory threshold container alerts"
            ]
            summary = "General remediation recommendations to restart and monitor the affected services."

        return {
            "immediate_actions": immediate,
            "permanent_fixes": permanent,
            "prevention_steps": prevention,
            "summary": summary
        }
