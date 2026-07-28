"""Historical incident vector search tool."""
from typing import Any, Dict
from .base import BaseTool
from ..memory.retriever import KnowledgeRetriever


class SearchHistoryTool(BaseTool):
    """Tool querying organizational vector memory for analogous historical incidents."""
    def __init__(self, retriever: KnowledgeRetriever = None):
        super().__init__()
        self.retriever = retriever or KnowledgeRetriever()

    @property
    def name(self) -> str:
        return "search_history"

    @property
    def description(self) -> str:
        return "Search vector repository for previous investigations exhibiting similar drift symptoms."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "model_id": {"type": "string"},
                "anomaly_type": {"type": "string"},
            },
            "required": ["model_id", "anomaly_type"],
        }

    async def invoke(self, **kwargs: Any) -> Dict[str, Any]:
        results = await self.retriever.query_incident_history(
            kwargs["model_id"], kwargs["anomaly_type"], limit=kwargs.get("limit", 3)
        )
        return {"similar_incidents": results}
