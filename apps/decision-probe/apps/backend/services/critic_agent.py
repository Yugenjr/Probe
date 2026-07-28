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

class CriticAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.use_real_client = GENAI_AVAILABLE and bool(self.api_key) and self.api_key != "dummy"
        
        if self.use_real_client:
            logger.info("Critic Agent initializing real GenAI Client.")
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("Critic Agent running in OFFLINE/MOCK mode.")
            self.client = None

    async def review_hypotheses(
        self,
        hypotheses: List[Dict[str, Any]],
        timeline: Dict[str, Any],
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Reviews each hypothesis for strengths, weaknesses, gaps, and confidence adjustments.
        """
        if not self.use_real_client:
            logger.info("Using offline mock critic agent.")
            return self._generate_mock_reviews(hypotheses)

        chunks_str = ""
        for idx, chk in enumerate(chunks):
            chunk_id = chk.get("id", f"chunk_{idx}")
            title = chk.get("title", "Unknown File")
            content = chk.get("snippet", chk.get("content", ""))
            chunks_str += f"--- START CHUNK ID: {chunk_id} (Source: {title}) ---\n{content}\n--- END CHUNK ---\n\n"

        prompt = f"""You are the Critic Agent inside Decision Probe.
Your responsibility is to analyze the generated hypotheses against the timeline and the raw evidence chunks to identify logical flaws, gaps, and contradictions.

Hypotheses to Review: {json.dumps(hypotheses)}
Incident Timeline: {json.dumps(timeline)}

Retrieved Evidence Chunks:
{chunks_str}

CRITICAL RULES:
1. For every hypothesis, you must output a review object specifying:
   - "hypothesis_id": The exact ID of the reviewed hypothesis (e.g. hyp_1)
   - "strengths": List of strings detailing what evidence supports this hypothesis
   - "weaknesses": List of strings detailing gaps, contradictions, or unsupported assumptions
   - "missing_information": List of strings describing files, logs, or metrics that are missing but needed to prove this hypothesis
   - "confidence_adjustment": A floating point number (usually between -0.30 and +0.10) that adjusts the hypothesis confidence
2. The Critic Agent must NEVER create new hypotheses. Only critique existing ones.
3. Every statement must reference timeline facts or raw evidence chunks.
4. Output MUST be a single raw JSON object matching the schema below (do not wrap in markdown codeblocks):

Expected JSON Output Schema:
{{
  "reviews": [
    {{
      "hypothesis_id": "hyp_1",
      "strengths": ["Strongly supported by connection timeout log in chunk_2"],
      "weaknesses": ["Assumes traffic spike occurred, but request logs are missing in workspace"],
      "missing_information": ["Web gateway concurrent request logs"],
      "confidence_adjustment": -0.05
    }}
  ]
}}
"""
        try:
            logger.info("Calling Gemini API to review hypotheses.")
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
            logger.error(f"Failed to critique hypotheses via Gemini: {e}. Falling back to mock reviews.")
            return self._generate_mock_reviews(hypotheses)

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()
        
        parsed = json.loads(raw_text)
        return {
            "reviews": parsed.get("reviews", [])
        }

    def _generate_mock_reviews(self, hypotheses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Deterministic mock reviewer of hypotheses.
        """
        reviews = []
        for hyp in hypotheses:
            hyp_id = hyp.get("id", "unknown")
            title_lower = hyp.get("title", "").lower()
            
            if "pool" in title_lower or "limit" in title_lower:
                reviews.append({
                    "hypothesis_id": hyp_id,
                    "strengths": ["Directly explains connection limit logs and error events in timeline"],
                    "weaknesses": ["Assumes active client request count was high without concurrent log evidence"],
                    "missing_information": ["Web application request load profiles", "PostgreSQL configuration metrics"],
                    "confidence_adjustment": -0.05
                })
            elif "deploy" in title_lower or "config" in title_lower:
                reviews.append({
                    "hypothesis_id": hyp_id,
                    "strengths": ["Correlates chronologically with deployment event preceding incident"],
                    "weaknesses": ["Database error logs do not show parameter mismatch or authentication denials"],
                    "missing_information": ["Deployment configuration manifests", "Database environment variables"],
                    "confidence_adjustment": -0.15
                })
            else:
                reviews.append({
                    "hypothesis_id": hyp_id,
                    "strengths": ["Plausible system failures"],
                    "weaknesses": ["Lacks direct logs indicating firewall or socket drops"],
                    "missing_information": ["Network route statistics", "Traceroute history"],
                    "confidence_adjustment": -0.20
                })
                
        return {"reviews": reviews}
