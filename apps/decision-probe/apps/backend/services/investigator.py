import os
import json
import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Try importing google-genai
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-genai is not available. Investigator agent will run in offline mock mode.")

class Investigator:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.use_real_client = GENAI_AVAILABLE and bool(self.api_key) and self.api_key != "dummy"
        
        if self.use_real_client:
            logger.info("Investigator Agent initializing real GenAI Client.")
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("Investigator Agent initialized in OFFLINE/MOCK mode.")
            self.client = None

    async def investigate(
        self, 
        plan: Dict[str, Any], 
        chunks: List[Dict[str, Any]], 
        workspace_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes the investigation facts extraction using Gemini or offline mock fallback.
        """
        if not self.use_real_client:
            logger.info("Using offline mock investigator.")
            return self._generate_mock_events(chunks)

        # Format retrieved evidence chunks
        chunks_str = ""
        for idx, chk in enumerate(chunks):
            chunk_id = chk.get("id", f"chunk_{idx}")
            title = chk.get("title", "Unknown File")
            content = chk.get("snippet", chk.get("content", ""))
            chunks_str += f"--- START CHUNK ID: {chunk_id} (Source: {title}) ---\n{content}\n--- END CHUNK ---\n\n"

        prompt = f"""You are the Lead Investigator Agent inside Decision Probe.
Your job is to transform retrieved evidence into structured investigation facts (events).

Workspace Metadata: {json.dumps(workspace_metadata)}
Investigation Plan: {json.dumps(plan)}

Retrieved Evidence Chunks:
{chunks_str}

CRITICAL RULES:
1. Extract ONLY facts explicitly supported by the evidence chunks.
2. Every event MUST reference the originating chunk in the "source_chunk" field (use the exact Chunk ID provided).
3. Do NOT perform Root Cause Analysis (RCA) or speculate on why something happened.
4. Do NOT invent events or summarize documents in prose.
5. If no clear facts or timestamps are found, return an empty events list.
6. Output MUST be a single raw JSON object matching the schema below (do not wrap in markdown codeblocks):

Expected JSON Output Schema:
{{
  "events": [
    {{
      "timestamp": "ISO-8601 formatted timestamp, e.g. 2026-07-24T10:41:12Z",
      "type": "event_type, e.g. error, warning, deployment, alert, config_change",
      "service": "affected service or system name, e.g. payments, auth, unknown",
      "description": "Short factual description of what occurred, directly quoting or citing the evidence",
      "source_chunk": "The exact ID of the chunk this event was extracted from"
    }}
  ]
}}
"""
        try:
            logger.info("Calling Gemini API to extract investigation events.")
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
            logger.error(f"Failed to extract events via Gemini API: {e}. Falling back to mock extraction.")
            return self._generate_mock_events(chunks)

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()
        
        parsed = json.loads(raw_text)
        return {
            "events": parsed.get("events", [])
        }

    def _generate_mock_events(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parses text chunks using simple heuristics and regex to generate realistic,
        factual events. Matches ISO timestamps in logs.
        """
        events = []
        # ISO timestamp matching pattern: 2026-07-24T10:41:12Z or 2026-07-24 10:41:12
        ts_pattern = re.compile(r"(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)")
        
        for idx, chunk in enumerate(chunks):
            chunk_id = chunk.get("id", f"chunk_{idx}")
            title = chunk.get("title", "billing_logs.log")
            content = chunk.get("snippet", chunk.get("content", ""))
            
            lines = content.split("\n")
            for line in lines:
                line_stripped = line.strip()
                if not line_stripped:
                    continue
                
                # Check for timestamp
                match = ts_pattern.search(line_stripped)
                if match:
                    timestamp = match.group(1)
                    # Normalize simple space separator to T and ensure Z suffix
                    timestamp_norm = timestamp.replace(" ", "T")
                    if not timestamp_norm.endswith("Z") and "+" not in timestamp_norm:
                        timestamp_norm += "Z"
                        
                    # Extract service if enclosed in brackets, e.g. [payments] or [billing]
                    service = "unknown"
                    srv_match = re.search(r"\[([a-zA-Z0-9_\-]+)\]", line_stripped)
                    if srv_match:
                        service = srv_match.group(1)
                    elif "billing" in line_stripped.lower():
                        service = "billing"
                    elif "payment" in line_stripped.lower():
                        service = "payments"
                    elif "database" in line_stripped.lower() or "db" in line_stripped.lower():
                        service = "database"
                        
                    # Determine type
                    event_type = "info"
                    if "error" in line_stripped.lower() or "timeout" in line_stripped.lower() or "failed" in line_stripped.lower():
                        event_type = "error"
                    elif "warning" in line_stripped.lower() or "warn" in line_stripped.lower():
                        event_type = "warning"
                    elif "deploy" in line_stripped.lower() or "release" in line_stripped.lower():
                        event_type = "deployment"
                        
                    # Strip timestamp and service from description to make it look clean
                    description = line_stripped
                    description = ts_pattern.sub("", description).strip()
                    if srv_match:
                        description = description.replace(srv_match.group(0), "").strip()
                    # Clean up remaining prefixes
                    description = re.sub(r"^[\s\-:：,\u2014]+", "", description).strip()
                    
                    events.append({
                        "timestamp": timestamp_norm,
                        "type": event_type,
                        "service": service,
                        "description": description if description else line_stripped,
                        "source_chunk": chunk_id
                    })
        
        # If no regex timestamps found, create standard fallback events from chunk summaries
        if not events:
            for idx, chunk in enumerate(chunks):
                chunk_id = chunk.get("id", f"chunk_{idx}")
                content = chunk.get("snippet", chunk.get("content", ""))
                
                event_type = "error" if "error" in content.lower() or "fail" in content.lower() else "info"
                service = "billing" if "billing" in content.lower() else "payments" if "payment" in content.lower() else "system"
                
                events.append({
                    "timestamp": "2026-07-28T12:00:00Z",
                    "type": event_type,
                    "service": service,
                    "description": content[:120].strip() + ("..." if len(content) > 120 else ""),
                    "source_chunk": chunk_id
                })
                
        # If no chunks at all, return empty list
        return {"events": events}
