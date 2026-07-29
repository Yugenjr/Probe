"""KnowledgeRepository — all filesystem I/O for the Knowledge MCP server.

The KnowledgeServer delegates every storage operation here.
It knows nothing about files, paths, or JSON.

When storage migrates from filesystem to Postgres, Qdrant, S3, or MinIO,
only this file changes. The server, tools, and gateway are unaffected.

Storage layout:
    storage/knowledge/
        documents/       → JSON knowledge articles
        runbooks/        → Markdown operational runbooks
        investigations/  → (reserved: future ingestion of investigation exports)
        reports/         → (reserved: future ingestion of compiled reports)
        architecture/    → (reserved: future ADRs and design docs)
"""
import json
import re
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class KnowledgeRepository:
    """Filesystem-backed knowledge repository.

    All methods return plain Python dicts/lists — no Pydantic models.
    The server and tools compose the results into ToolResult objects.
    """

    def __init__(self, base_dir: str = "storage/knowledge") -> None:
        self._base = Path(base_dir)
        self._documents_dir = self._base / "documents"
        self._runbooks_dir = self._base / "runbooks"
        self._investigations_dir = self._base / "investigations"
        self._reports_dir = self._base / "reports"
        self._architecture_dir = self._base / "architecture"

        for directory in [
            self._documents_dir,
            self._runbooks_dir,
            self._investigations_dir,
            self._reports_dir,
            self._architecture_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Documents
    # ------------------------------------------------------------------

    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Full-text keyword search over JSON knowledge articles.

        Matches against title, content, and tags. Case-insensitive.
        Each query word is OR-matched — any match returns the document.
        """
        keywords = [kw for kw in query.lower().split() if kw]
        if not keywords:
            return []

        results = []
        for fpath in sorted(self._documents_dir.glob("*.json")):
            try:
                data = json.loads(fpath.read_text(encoding="utf-8"))
                # Build a flat search corpus from the document
                corpus = " ".join([
                    str(data.get("title", "")),
                    str(data.get("content", "")),
                    " ".join(data.get("tags", [])),
                    " ".join(data.get("categories", [])),
                ]).lower()
                if any(kw in corpus for kw in keywords):
                    results.append(data)
            except Exception as exc:
                logger.debug("Skipping malformed document %s: %s", fpath.name, exc)
                continue

        return results[:limit]

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Load a single document by ID (filename without .json extension)."""
        # Sanitise: reject any path traversal attempts
        safe_id = Path(doc_id).name
        fpath = self._documents_dir / f"{safe_id}.json"
        if not fpath.exists():
            logger.debug("Document not found: %s", doc_id)
            return None
        try:
            return json.loads(fpath.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.error("Failed to load document %s: %s", doc_id, exc)
            return None

    def list_documents(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List document metadata without returning full content bodies."""
        results = []
        for fpath in sorted(self._documents_dir.glob("*.json"))[:limit]:
            try:
                data = json.loads(fpath.read_text(encoding="utf-8"))
                results.append({
                    "id": data.get("id", fpath.stem),
                    "title": data.get("title", ""),
                    "category": data.get("category", ""),
                    "tags": data.get("tags", []),
                    "updated_at": data.get("updated_at", ""),
                })
            except Exception:
                continue
        return results

    # ------------------------------------------------------------------
    # Investigation history
    # ------------------------------------------------------------------

    def search_investigations(
        self,
        query: str = "",
        model_id: str = "",
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search completed InvestigationSession records from live session storage.

        Filters by:
          - status == 'completed'
          - model_id substring match (if provided)
          - keyword match across full session JSON (if query provided)

        Returns lightweight summary dicts, not full session payloads.
        """
        sessions_dir = Path("storage/sessions")
        if not sessions_dir.exists():
            return []

        query_keywords = [kw for kw in query.lower().split() if kw]
        model_lower = model_id.lower()
        results = []

        for fpath in sessions_dir.glob("*.json"):
            try:
                data = json.loads(fpath.read_text(encoding="utf-8"))
                # Only completed sessions provide meaningful historical context
                if data.get("status", "").lower() != "completed":
                    continue

                incident = data.get("incident") or {}
                session_model = incident.get("model_id", "").lower()

                # Filter by model
                if model_lower and model_lower not in session_model:
                    continue

                # Filter by keyword query
                if query_keywords:
                    haystack = json.dumps(data).lower()
                    if not any(kw in haystack for kw in query_keywords):
                        continue

                hypotheses = data.get("hypotheses") or []
                evaluation = data.get("evaluation_result") or {}
                results.append({
                    "session_id": data.get("session_id", ""),
                    "model_id": session_model,
                    "severity": incident.get("severity", ""),
                    "started_at": data.get("started_at", ""),
                    "completed_at": data.get("completed_at", ""),
                    "confidence": evaluation.get("confidence", 0.0),
                    "hypothesis_count": len(hypotheses),
                    "top_hypothesis": (
                        hypotheses[0].get("statement", "") if hypotheses else ""
                    ),
                    "recommendation_count": len(
                        evaluation.get("recommended_actions", [])
                    ),
                })
            except Exception as exc:
                logger.debug("Skipping session file %s: %s", fpath.name, exc)
                continue

        # Most recent first (completed_at descending)
        results.sort(key=lambda x: x.get("completed_at", ""), reverse=True)
        return results[:limit]

    # ------------------------------------------------------------------
    # Runbooks
    # ------------------------------------------------------------------

    def search_runbooks(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Keyword search across operational runbook markdown files."""
        keywords = [kw for kw in query.lower().split() if kw]
        if not keywords:
            return []

        results = []
        for fpath in sorted(self._runbooks_dir.glob("*.md")):
            try:
                content = fpath.read_text(encoding="utf-8")
                if not any(kw in content.lower() for kw in keywords):
                    continue
                # Extract first # heading as title
                title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else fpath.stem
                # First 400 chars as excerpt
                excerpt = content[:400].replace("\n", " ").strip()
                results.append({
                    "id": fpath.stem,
                    "title": title,
                    "excerpt": excerpt,
                    "full_content": content,
                })
            except Exception as exc:
                logger.debug("Skipping runbook %s: %s", fpath.name, exc)
                continue

        return results[:limit]
