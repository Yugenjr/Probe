"""Capability-based planning registry for DriftGuard Probe."""
import logging
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class CapabilityRequest(BaseModel):
    """Planner-requested capability required during investigative steps."""
    capability: str = Field(..., description="Target capability key, e.g., 'runbooks'")
    priority: int = Field(default=1, description="Priority rating (1=highest)")
    required: bool = Field(default=True, description="Whether capability is hard requirement")
    status: str = Field(default="pending", description="Status of retrieval")


class EvidencePlan(BaseModel):
    """Structured plan produced by Planner detailing required capabilities."""
    goal: str = Field(..., description="High-level investigative goal")
    capabilities: List[CapabilityRequest] = Field(default_factory=list)


class CapabilityRegistry:
    """Registry mapping symbolic capabilities to concrete servers and tools dynamically."""
    
    def __init__(self):
        # Default mapping of capability key -> list of (server_name, tool_name)
        self._mappings: Dict[str, List[tuple[str, str]]] = {
            "runbooks": [("knowledge", "search_runbooks")],
            "historical_investigations": [("knowledge", "search_investigations")],
            "knowledge_base": [("knowledge", "search_documents")],
            "code_history": [("github", "search_commits"), ("github", "list_issues")],
            "commits": [("github", "search_commits")],
            "pull_requests": [("github", "list_pull_requests")],
            "experiment_traces": [("mlflow", "search_runs"), ("mlflow", "get_metric_history")],
            "model_registry": [("mlflow", "get_registered_model")],
            "runs": [("mlflow", "search_runs")],
        }

    def register_capability(self, capability: str, server_name: str, tool_name: str):
        """Register a new server capability mapping."""
        if capability not in self._mappings:
            self._mappings[capability] = []
        self._mappings[capability].append((server_name, tool_name))
        logger.info("[CapabilityRegistry] Mapped capability '%s' to server '%s' tool '%s'", capability, server_name, tool_name)

    def resolve(self, capability: str) -> List[tuple[str, str]]:
        """Resolve a capability to satisfying providers (server, tool)."""
        return self._mappings.get(capability, [])

    def get_supported_capabilities(self) -> List[str]:
        """Return list of all registered capabilities."""
        return list(self._mappings.keys())
