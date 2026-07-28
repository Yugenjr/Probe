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

class EvidenceFusionAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.use_real_client = GENAI_AVAILABLE and bool(self.api_key) and self.api_key != "dummy"
        
        if self.use_real_client:
            logger.info("Evidence Fusion Agent initializing real GenAI Client.")
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("Evidence Fusion Agent running in OFFLINE/MOCK mode.")
            self.client = None

    async def fuse_evidence(
        self,
        existing_chunks: List[Dict[str, Any]],
        logs: Dict[str, Any],
        metrics: Dict[str, Any],
        deployments: Dict[str, Any],
        git_changes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merges existing document evidence chunks with logs, metrics, deployments,
        and Git change histories. Returns normalized fused chunks and evidence graph updates.
        """
        if not self.use_real_client:
            logger.info("Using offline mock evidence fusion agent.")
            return self._generate_mock_fusion(logs, metrics, deployments, git_changes)

        prompt = f"""You are the Evidence Fusion Agent inside Decision Probe.
Your responsibility is to merge existing workspace evidence chunks with external application logs, observability metrics, deployment details, and git code changes.

Existing Chunks: {json.dumps(existing_chunks)}
External Logs: {json.dumps(logs)}
Metrics Data: {json.dumps(metrics)}
Deployments Data: {json.dumps(deployments)}
Git Commits Data: {json.dumps(git_changes)}

CRITICAL RULES:
1. Merge the feeds and rank them based on relevance_score (0.0 to 1.0) explaining the connection.
2. Build matching graph update nodes and edges using these Node types:
   - "Service", "Deployment", "Commit", "Metric", "Alert"
   and Edge types:
   - "caused_by", "deployed_before", "correlated_with", "affected_service"
3. Output MUST be a single raw JSON object matching the schema below (do not wrap in markdown codeblocks):

Expected JSON Output Schema:
{{
  "new_evidence_chunks": [
    {{
      "source": "Log line / Prometheus / Git commit",
      "content": "Description of the event/metric value",
      "relevance_score": 0.95
    }}
  ],
  "graph_updates": [
    {{
      "nodes": [
        {{ "id": "node_payments_service", "type": "Service", "label": "payments service" }}
      ],
      "edges": [
        {{ "source": "node_payment_deploy", "target": "node_payments_service", "type": "affected_service" }}
      ]
    }}
  ]
}}
"""
        try:
            logger.info("Calling Gemini API to fuse external evidence.")
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
            logger.error(f"Failed to fuse evidence via Gemini: {e}. Falling back to mock fusion.")
            return self._generate_mock_fusion(logs, metrics, deployments, git_changes)

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()
        
        parsed = json.loads(raw_text)
        return {
            "new_evidence_chunks": parsed.get("new_evidence_chunks", []),
            "graph_updates": parsed.get("graph_updates", [])
        }

    def _generate_mock_fusion(
        self,
        logs: Dict[str, Any],
        metrics: Dict[str, Any],
        deployments: Dict[str, Any],
        git_changes: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Build mock chunks
        new_chunks = []
        for l in logs.get("logs", []):
            new_chunks.append({
                "source": f"Log Collector: {l.get('service')}",
                "content": f"[{l.get('level')}] {l.get('message')}",
                "relevance_score": 0.90
            })
        for m in metrics.get("metrics", []):
            new_chunks.append({
                "source": "Prometheus Metrics",
                "content": f"Metric {m.get('name')} value reached {m.get('value')}",
                "relevance_score": 0.85
            })
        for d in deployments.get("changes", []):
            new_chunks.append({
                "source": "Deployment History",
                "content": f"Service {d.get('service')} deployed version {d.get('version')} by {d.get('author')}: {d.get('summary')}",
                "relevance_score": 0.80
            })
        for g in git_changes.get("commits", []):
            new_chunks.append({
                "source": "Git Commits",
                "content": f"Commit {g.get('hash')} by {g.get('author')}: {g.get('message')} ({', '.join(g.get('files_changed', []))})",
                "relevance_score": 0.75
            })

        # Build mock graph updates
        nodes = [
            {"id": "node_payments_service", "type": "Service", "label": "payments-service"},
            {"id": "node_payment_deploy", "type": "Deployment", "label": "Argocd v1.1.0"},
            {"id": "node_payments_commit", "type": "Commit", "label": "commit a4f8d29b"},
            {"id": "node_payments_metric", "type": "Metric", "label": "db_connections usage (98%)"}
        ]
        edges = [
            {"source": "node_payment_deploy", "target": "node_payments_service", "type": "affected_service"},
            {"source": "node_payments_commit", "target": "node_payment_deploy", "type": "deployed_before"},
            {"source": "node_payments_metric", "target": "node_payments_service", "type": "correlated_with"}
        ]

        return {
            "new_evidence_chunks": new_chunks,
            "graph_updates": [{
                "nodes": nodes,
                "edges": edges
            }]
        }
