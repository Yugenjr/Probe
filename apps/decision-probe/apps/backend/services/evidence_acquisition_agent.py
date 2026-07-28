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

class EvidenceAcquisitionAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.use_real_client = GENAI_AVAILABLE and bool(self.api_key) and self.api_key != "dummy"
        
        if self.use_real_client:
            logger.info("Evidence Acquisition Agent initializing real GenAI Client.")
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("Evidence Acquisition Agent running in OFFLINE/MOCK mode.")
            self.client = None

    async def generate_requests(
        self,
        gaps: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Converts missing evidence gaps into specific, actionable data request queries.
        """
        evidence_gaps = gaps.get("evidence_gaps", [])
        if not evidence_gaps:
            return {"requests": []}

        if not self.use_real_client:
            logger.info("Using offline mock evidence acquisition agent.")
            return self._generate_mock_requests(evidence_gaps)

        prompt = f"""You are the Evidence Acquisition Agent inside Decision Probe.
Your responsibility is to convert a list of missing evidence gaps into structured, actionable collection queries.

Evidence Gaps: {json.dumps(evidence_gaps)}

CRITICAL RULES:
1. For each gap, formulate a precise metric query, config lookup, trace lookup, or log search string.
2. Define:
   - "type": "log" or "metric" or "config" or "trace"
   - "source": Target observability system (e.g. Jaeger, Prometheus, PostgreSQL configuration)
   - "query": Actionable search query or configuration option parameter
   - "time_range": Time range window (e.g., "10:00-11:00 UTC")
3. Output MUST be a single raw JSON object matching the schema below (do not wrap in markdown codeblocks):

Expected JSON Output Schema:
{{
  "requests": [
    {{
      "type": "metric",
      "source": "PostgreSQL monitoring",
      "query": "connection usage during incident window",
      "time_range": "10:00-11:00 UTC"
    }}
  ]
}}
"""
        try:
            logger.info("Calling Gemini API to generate evidence acquisition requests.")
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
            logger.error(f"Failed to generate requests via Gemini: {e}. Falling back to mock acquisition requests.")
            return self._generate_mock_requests(evidence_gaps)

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()
        
        parsed = json.loads(raw_text)
        return {
            "requests": parsed.get("requests", [])
        }

    def _generate_mock_requests(self, evidence_gaps: List[Dict[str, Any]]) -> Dict[str, Any]:
        requests = []
        for gap in evidence_gaps:
            gap_title = gap.get("gap", "").lower()
            source = gap.get("required_source", "Observability System")
            
            if "metric" in gap_title:
                req_type = "metric"
                query = "connection usage during incident window"
                time_range = "10:00-11:00 UTC"
            elif "config" in gap_title or "settings" in gap_title:
                req_type = "config"
                query = "inspect environment variables and limits setting configuration"
                time_range = "last deployment window"
            elif "log" in gap_title:
                req_type = "log"
                query = "error level events from payments pods"
                time_range = "10:00-11:00 UTC"
            else:
                req_type = "trace"
                query = "get trace details for http service dependencies"
                time_range = "10:00-11:00 UTC"

            requests.append({
                "type": req_type,
                "source": source,
                "query": query,
                "time_range": time_range
            })
            
        return {"requests": requests}
