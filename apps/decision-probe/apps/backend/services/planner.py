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
    logger.warning("google-genai is not available. Planner agent will run in offline mock mode.")

class Planner:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.use_real_client = GENAI_AVAILABLE and bool(self.api_key) and self.api_key != "dummy"
        
        if self.use_real_client:
            logger.info("Planner Agent initializing real GenAI Client.")
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("Planner Agent initialized in OFFLINE/MOCK mode.")
            self.client = None

    async def plan(self, goal: str, workspace_title: str, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates a structured InvestigationPlan.
        Inputs:
          - goal: The investigation goal / prompt.
          - workspace_title: Title of the workspace.
          - chunks: Retrieved evidence chunks (List of dicts).
        Returns a dict matching:
          {
            "objectives": List[str],
            "questions": List[str],
            "evidence_needed": List[str],
            "priority": str ("high" | "medium" | "low")
          }
        """
        if not self.use_real_client:
            logger.info("Using offline mock planner.")
            return self._generate_mock_plan(goal, chunks)

        chunks_str = ""
        for idx, chk in enumerate(chunks):
            title = chk.get("title", "Unknown Source")
            snippet = chk.get("snippet", chk.get("content", ""))
            chunks_str += f"--- Evidence Chunk {idx + 1} ({title}) ---\n{snippet}\n\n"

        prompt = f"""You are the Lead Planning Agent inside the Decision Probe investigation engine.
Your sole job is to design the strategy for an investigation.

Workspace Title: {workspace_title}
Investigation Goal: {goal}

Retrieved Evidence:
{chunks_str}

Rules:
1. Determine ONLY the investigation strategy (objectives, questions, evidence_needed, and priority).
2. Do NOT perform root cause analysis (RCA).
3. Do NOT generate timelines or invent evidence.
4. Do NOT summarize the documents.
5. Your output must be a single JSON object.

Expected JSON format:
{{
  "objectives": ["core objective 1", "core objective 2"],
  "questions": ["critical question 1", "critical question 2"],
  "evidence_needed": ["additional evidence type 1", "additional evidence type 2"],
  "priority": "high" or "medium" or "low"
}}
"""
        try:
            logger.info("Calling Gemini API to generate investigation plan.")
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            raw_text = response.text
            return self._parse_json(raw_text)
        except Exception as e:
            logger.error(f"Failed to generate plan via Gemini API: {e}. Falling back to mock plan.")
            return self._generate_mock_plan(goal, chunks)

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()
        
        parsed = json.loads(raw_text)
        
        # Enforce basic validation
        validated = {
            "objectives": parsed.get("objectives", []),
            "questions": parsed.get("questions", []),
            "evidence_needed": parsed.get("evidence_needed", []),
            "priority": parsed.get("priority", "medium").lower()
        }
        if validated["priority"] not in ("high", "medium", "low"):
            validated["priority"] = "medium"
            
        return validated

    def _generate_mock_plan(self, goal: str, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        goal_lower = goal.lower()
        priority = "medium"
        if any(w in goal_lower for w in ("outage", "down", "critical", "incident", "failure", "crash", "prod", "high", "restart", "restarts", "memory")):
            priority = "high"
        elif any(w in goal_lower for w in ("test", "sandbox", "low", "debug")):
            priority = "low"

        return {
            "objectives": [
                f"Define scope and objectives for: '{goal}'",
                "Perform initial analysis of the retrieved evidence logs and text snippets",
                "Verify system state transitions and potential data anomalies"
            ],
            "questions": [
                f"What component failure initiated '{goal}'?",
                "Are there correlating timestamp logs in the workspace documents?",
                "What environment parameters might have introduced this behavior?"
            ],
            "evidence_needed": [
                "Related service telemetry and memory dump statistics",
                "Recent Git changes and deployment manifest revisions",
                "Historical runbooks and API documentation matching the logs"
            ],
            "priority": priority
        }


class LegacyPlanner:
    def plan(self, context) -> Any:
        from services.models import ExecutionPlan
        prompt = context.user_prompt.lower()
        plan = ExecutionPlan()

        if "search" in prompt or "web" in prompt or "online" in prompt:
            plan.retrieve_web = True

        if "doc" in prompt or "manual" in prompt or "api" in prompt:
            plan.retrieve_documents = True
            
        if "history" in prompt or "previous" in prompt or "before" in prompt:
            plan.retrieve_workspace_history = True
            
        if "summarize" in prompt or "tldr" in prompt:
            plan.generate_summary = True

        return plan

