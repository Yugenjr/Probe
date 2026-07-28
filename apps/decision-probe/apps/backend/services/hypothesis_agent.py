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

class HypothesisAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.use_real_client = GENAI_AVAILABLE and bool(self.api_key) and self.api_key != "dummy"
        
        if self.use_real_client:
            logger.info("Hypothesis Agent initializing real GenAI Client.")
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("Hypothesis Agent running in OFFLINE/MOCK mode.")
            self.client = None

    async def generate_hypotheses(
        self,
        plan: Dict[str, Any],
        timeline: Dict[str, Any],
        evidence: Dict[str, Any],
        graph: Dict[str, Any],
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generates 2-5 structured incident hypotheses grounded in retrieved evidence.
        """
        if not self.use_real_client:
            logger.info("Using offline mock hypothesis agent.")
            return self._generate_mock_hypotheses(timeline, chunks)

        chunks_str = ""
        for idx, chk in enumerate(chunks):
            chunk_id = chk.get("id", f"chunk_{idx}")
            title = chk.get("title", "Unknown File")
            content = chk.get("snippet", chk.get("content", ""))
            chunks_str += f"--- START CHUNK ID: {chunk_id} (Source: {title}) ---\n{content}\n--- END CHUNK ---\n\n"

        prompt = f"""You are the Hypothesis Agent inside Decision Probe.
Your responsibility is to analyze the following timeline, evidence, graph structure, and text chunks to generate multiple possible explanations (hypotheses) for the incident.

Investigation Plan: {json.dumps(plan)}
Incident Timeline: {json.dumps(timeline)}
Evidence Facts: {json.dumps(evidence)}
Graph Structure: {json.dumps(graph)}

Retrieved Evidence Chunks:
{chunks_str}

CRITICAL RULES:
1. Generate between 2 and 5 hypotheses.
2. Every hypothesis MUST include an id, title, description, list of supporting_evidence chunk IDs, confidence (float 0.0 to 1.0), and assumptions.
3. Every statement must reference at least one retrieved chunk ID in "supporting_evidence". Do NOT invent evidence or speculate without references.
4. Do NOT select a winning hypothesis in this stage. Just present the alternatives.
5. Output MUST be a single raw JSON object matching the schema below (do not wrap in markdown codeblocks):

Expected JSON Output Schema:
{{
  "hypotheses": [
    {{
      "id": "hyp_1",
      "title": "Short descriptive title, e.g. Connection Pool Exhaustion",
      "description": "Factual description of the hypothesis, linking it to the chunks",
      "supporting_evidence": ["chunk_id_1", "chunk_id_2"],
      "confidence": 0.80,
      "assumptions": ["List of assumptions required for this hypothesis to hold, e.g. Active client traffic was high"]
    }}
  ]
}}
"""
        try:
            logger.info("Calling Gemini API to generate hypotheses.")
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
            logger.error(f"Failed to generate hypotheses via Gemini: {e}. Falling back to mock hypotheses.")
            return self._generate_mock_hypotheses(timeline, chunks)

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()
        
        parsed = json.loads(raw_text)
        return {
            "hypotheses": parsed.get("hypotheses", [])
        }

    def _generate_mock_hypotheses(self, timeline: Dict[str, Any], chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Deterministic mock generator of hypotheses based on timeline events.
        """
        events = timeline.get("events", [])
        chunk_ids = [c.get("id", f"chunk_{i}") for i, c in enumerate(chunks)]
        if not chunk_ids:
            chunk_ids = ["chunk_0"]

        # Default fallback hypotheses if timeline is empty
        if not events:
            return {
                "hypotheses": [
                    {
                        "id": "hyp_1",
                        "title": "System resource limits exceeded",
                        "description": "General system capacity or configuration limits were hit.",
                        "supporting_evidence": [chunk_ids[0]],
                        "confidence": 0.50,
                        "assumptions": ["A spike in background requests occurred"]
                    },
                    {
                        "id": "hyp_2",
                        "title": "Network boundary disconnect",
                        "description": "Network partition or transient firewall disconnect occurred.",
                        "supporting_evidence": [chunk_ids[0]],
                        "confidence": 0.35,
                        "assumptions": ["Temporary switch or packet drop issue"]
                    }
                ]
            }

        # Analyze errors
        error_events = [e for e in events if e.get("type") == "error"]
        service_name = error_events[0].get("service", "payments") if error_events else "payments"
        desc = error_events[0].get("description", "") if error_events else "Database connection timed out"
        ref_chunk = error_events[0].get("source_chunk", chunk_ids[0]) if error_events else chunk_ids[0]

        h1_title = "Database connection pool exhaustion"
        h1_desc = f"Primary database connection limits exceeded in '{service_name}' service due to request volume or pool configuration limits."
        
        h2_title = "Network timeout or firewall drop"
        h2_desc = f"A network drop or database firewall policy adjustment interrupted the socket communication of the '{service_name}' service."

        # If a deployment event is found, customize hypothesis 2 to deployment rollback / config issue
        deploy_events = [e for e in events if e.get("type") == "deployment"]
        if deploy_events:
            h2_title = "Broken deployment configuration update"
            h2_desc = f"The deployment of service '{deploy_events[0].get('service')}' introduced a bad database configuration parameter (e.g. invalid URI or low timeout)."
            ref_chunk2 = deploy_events[0].get("source_chunk", ref_chunk)
        else:
            ref_chunk2 = ref_chunk

        return {
            "hypotheses": [
                {
                    "id": "hyp_1",
                    "title": h1_title,
                    "description": h1_desc,
                    "supporting_evidence": [ref_chunk],
                    "confidence": 0.80,
                    "assumptions": ["Connection pool size was configured too low", "Concurrent user requests increased"]
                },
                {
                    "id": "hyp_2",
                    "title": h2_title,
                    "description": h2_desc,
                    "supporting_evidence": [ref_chunk2],
                    "confidence": 0.50,
                    "assumptions": ["Database parameters were changed in the latest deployment"]
                }
            ]
        }
