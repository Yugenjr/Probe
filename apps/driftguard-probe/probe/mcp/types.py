"""Shared MCP type contracts.

Every MCP server returns ToolResult.
Every tool exposes ToolDefinition for discovery.
Every dispatch is a ToolRequest.

These types are the lingua franca of the entire MCP layer — GitHub, Prometheus,
MLflow, Knowledge all speak exactly this language.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """Structured result returned by every MCP tool invocation.

    Whether the tool called the Knowledge base, GitHub, Prometheus, or MLflow,
    the Investigator always receives exactly this shape.
    """
    success: bool = Field(..., description="Whether the tool executed without error")
    content: str = Field(..., description="Primary human-readable text content")
    artifacts: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Structured data artifacts (documents, metrics, events etc.)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Tool-level metadata: counts, source, page info etc."
    )
    execution_time_ms: int = Field(default=0, description="Wall-clock execution time in milliseconds")
    error: Optional[str] = Field(default=None, description="Error message when success=False")


class ToolDefinition(BaseModel):
    """Tool capability declaration exposed by a BaseMCPServer.

    The ToolGateway collects these from all registered servers so agents
    can discover what tools are available before deciding which to invoke.
    """
    name: str = Field(..., description="Unique tool name within its server namespace")
    description: str = Field(..., description="Natural-language description for LLM planning")
    parameters: Dict[str, Any] = Field(
        ...,
        description="JSON Schema describing accepted arguments"
    )
    server: str = Field(..., description="Name of the server that owns this tool")

    @property
    def qualified_name(self) -> str:
        """Fully qualified name: 'knowledge.search_documents'."""
        return f"{self.server}.{self.name}"


class ToolRequest(BaseModel):
    """Namespaced tool invocation request routed through the ServerRegistry.

    Explicit server + tool namespacing prevents ambiguity when multiple servers
    expose identically named tools (e.g., both Knowledge and GitHub expose search()).
    """
    server: str = Field(..., description="Target server name e.g. 'knowledge', 'github'")
    tool: str = Field(..., description="Tool name within that server")
    arguments: Dict[str, Any] = Field(
        default_factory=dict,
        description="Tool arguments matching the tool's parameter schema"
    )
