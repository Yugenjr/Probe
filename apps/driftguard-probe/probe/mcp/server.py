"""BaseMCPServer — abstract contract every MCP server must satisfy.

A server owns a namespace ('knowledge', 'github', 'prometheus') and a set of
tools. It receives raw tool calls and returns structured ToolResult objects.

The server knows nothing about:
  - How it was discovered (registry)
  - How its caller connected to it (transport)
  - How the agent uses the result (gateway)

Each of those concerns belongs to a different layer.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List
import logging

from .types import ToolResult, ToolDefinition

logger = logging.getLogger(__name__)


class BaseMCPServer(ABC):
    """Abstract base class every MCP server must implement.

    Implementing a new server (GitHub, Prometheus, MLflow) requires:
      1. Subclass BaseMCPServer
      2. Implement name, get_tools(), handle_tool_call()
      3. Register with ServerRegistry at startup

    No other code changes are required.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique server identifier used for namespaced routing.

        Examples: 'knowledge', 'github', 'prometheus', 'grafana', 'mlflow'
        """
        ...

    @abstractmethod
    def get_tools(self) -> List[ToolDefinition]:
        """Return all tool definitions this server exposes.

        Called by the registry during tool discovery. The ToolGateway
        aggregates these across all servers so agents can inspect what
        capabilities are available.
        """
        ...

    @abstractmethod
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Dispatch an incoming tool call to the appropriate handler.

        Args:
            tool_name: Name of the tool to invoke (unqualified, within this server).
            arguments: Key-value arguments matching the tool's parameter schema.

        Returns:
            ToolResult — always. Never raises. Unknown tools return success=False.
        """
        ...

    def __repr__(self) -> str:
        tools = [t.name for t in self.get_tools()]
        return f"<{self.__class__.__name__} name={self.name!r} tools={tools}>"
