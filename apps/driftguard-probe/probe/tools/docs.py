"""Enterprise documentation search tool."""
from typing import Any, Dict
from .base import BaseTool
from ..memory.retriever import KnowledgeRetriever


class SearchDocsTool(BaseTool):
    """Tool searching organizational runbooks, deployment guides, and feature definitions."""
    def __init__(self, retriever: KnowledgeRetriever = None):
        super().__init__()
        self.retriever = retriever or KnowledgeRetriever()

    @property
    def name(self) -> str:
        return "search_docs"

    @property
    def description(self) -> str:
        return "Retrieve relevant operational runbooks and data science pipeline documentation."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}

    async def invoke(self, **kwargs: Any) -> Dict[str, Any]:
        results = await self.retriever.search_documentation(kwargs["query"], limit=kwargs.get("limit", 3))
        return {"documentation_matches": results}
