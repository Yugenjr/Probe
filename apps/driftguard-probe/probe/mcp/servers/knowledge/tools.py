"""All Knowledge MCP tools — consolidated in one file.

Five tools, each ~30 lines. One file, not five.

Adding a sixth tool:
  1. Write the class here
  2. Add it to KnowledgeServer's _tools dict
  No other changes required.

Tools:
  - SearchDocumentsTool       full-text keyword search over articles
  - GetDocumentTool           fetch single article by ID
  - ListDocumentsTool         list document metadata
  - SearchInvestigationsTool  look up completed investigation history
  - SearchRunbooksTool        find relevant operational runbooks
"""
from typing import Any

from ...tools.base_tool import BaseMCPTool
from ...types import ToolResult, ToolDefinition
from .repository import KnowledgeRepository


class SearchDocumentsTool(BaseMCPTool):
    """Full-text keyword search over knowledge base articles."""

    def __init__(self, repo: KnowledgeRepository) -> None:
        self._repo = repo

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="search_documents",
            description=(
                "Search knowledge base articles using keyword matching. "
                "Use this to find relevant documentation, past incident analyses, "
                "and technical guides related to the current investigation."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search keywords (e.g. 'PSI drift feature distribution')",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default 5)",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
            server="knowledge",
        )

    async def execute(self, query: str = "", limit: int = 5, **kwargs: Any) -> ToolResult:
        docs = self._repo.search_documents(query, limit=limit)
        if not docs:
            return ToolResult(
                success=True,
                content=f"No knowledge base articles found matching '{query}'.",
                artifacts=[],
                metadata={"count": 0},
            )
        content = "\n\n".join(
            f"[{d.get('id', '')}] {d.get('title', '')}\n"
            f"Category: {d.get('category', 'General')} | "
            f"Tags: {', '.join(d.get('tags', []))}\n"
            f"{str(d.get('content', ''))[:400]}"
            for d in docs
        )
        return ToolResult(
            success=True,
            content=content,
            artifacts=docs,
            metadata={"count": len(docs), "query": query},
        )


class GetDocumentTool(BaseMCPTool):
    """Retrieve a single knowledge base article by its ID."""

    def __init__(self, repo: KnowledgeRepository) -> None:
        self._repo = repo

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_document",
            description=(
                "Retrieve the full content of a specific knowledge base article by ID."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "Document identifier (e.g. 'psi-drift-diagnosis')",
                    }
                },
                "required": ["doc_id"],
            },
            server="knowledge",
        )

    async def execute(self, doc_id: str = "", **kwargs: Any) -> ToolResult:
        doc = self._repo.get_document(doc_id)
        if not doc:
            return ToolResult(
                success=False,
                content="",
                error=f"Document '{doc_id}' not found in knowledge base.",
            )
        return ToolResult(
            success=True,
            content=str(doc.get("content", "")),
            artifacts=[doc],
            metadata={"id": doc_id, "title": doc.get("title", "")},
        )


class ListDocumentsTool(BaseMCPTool):
    """List all knowledge base documents with metadata."""

    def __init__(self, repo: KnowledgeRepository) -> None:
        self._repo = repo

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="list_documents",
            description="List all available knowledge base documents with their metadata.",
            parameters={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of documents to list (default 20)",
                        "default": 20,
                    }
                },
            },
            server="knowledge",
        )

    async def execute(self, limit: int = 20, **kwargs: Any) -> ToolResult:
        docs = self._repo.list_documents(limit=limit)
        if not docs:
            return ToolResult(
                success=True,
                content="No documents in knowledge base.",
                artifacts=[],
                metadata={"count": 0},
            )
        lines = [f"Found {len(docs)} documents:"] + [
            f"  [{d['id']}] {d['title']} ({d.get('category', '')})"
            for d in docs
        ]
        return ToolResult(
            success=True,
            content="\n".join(lines),
            artifacts=docs,
            metadata={"count": len(docs)},
        )


class SearchInvestigationsTool(BaseMCPTool):
    """Search completed past investigations by model ID or keyword."""

    def __init__(self, repo: KnowledgeRepository) -> None:
        self._repo = repo

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="search_investigations",
            description=(
                "Search historical completed investigations to find relevant precedents. "
                "Filter by model ID to find all past incidents for the same model, "
                "or use keywords to find investigations with similar drift patterns."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Keyword query (e.g. 'ADWIN covariate drift')",
                        "default": "",
                    },
                    "model_id": {
                        "type": "string",
                        "description": "Filter by model identifier for model-specific history",
                        "default": "",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results (default 5)",
                        "default": 5,
                    },
                },
            },
            server="knowledge",
        )

    async def execute(
        self, query: str = "", model_id: str = "", limit: int = 5, **kwargs: Any
    ) -> ToolResult:
        investigations = self._repo.search_investigations(
            query=query, model_id=model_id, limit=limit
        )
        if not investigations:
            return ToolResult(
                success=True,
                content="No relevant past investigations found.",
                artifacts=[],
                metadata={"count": 0},
            )
        lines = [f"Found {len(investigations)} past investigations:"] + [
            f"  [{i['session_id'][:12]}…] model={i['model_id']} "
            f"confidence={i['confidence']:.0%} hypotheses={i['hypothesis_count']}\n"
            f"    {i['top_hypothesis'][:120]}"
            for i in investigations
        ]
        return ToolResult(
            success=True,
            content="\n".join(lines),
            artifacts=investigations,
            metadata={"count": len(investigations)},
        )


class SearchRunbooksTool(BaseMCPTool):
    """Search operational runbooks for incident response playbooks."""

    def __init__(self, repo: KnowledgeRepository) -> None:
        self._repo = repo

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="search_runbooks",
            description=(
                "Search operational runbooks and incident response playbooks. "
                "Use this to find remediation procedures, escalation paths, "
                "and mitigation strategies relevant to the current incident type."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search keywords (e.g. 'rollback retrain drift')",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results (default 5)",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
            server="knowledge",
        )

    async def execute(self, query: str = "", limit: int = 5, **kwargs: Any) -> ToolResult:
        runbooks = self._repo.search_runbooks(query, limit=limit)
        if not runbooks:
            return ToolResult(
                success=True,
                content=f"No runbooks found matching '{query}'.",
                artifacts=[],
                metadata={"count": 0},
            )
        lines = [f"Found {len(runbooks)} runbooks:"] + [
            f"  [{r['id']}] {r['title']}\n    {r['excerpt'][:200]}"
            for r in runbooks
        ]
        return ToolResult(
            success=True,
            content="\n".join(lines),
            artifacts=runbooks,
            metadata={"count": len(runbooks)},
        )
