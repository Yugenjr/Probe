"""ToolGateway — the single interface agents use to invoke any MCP tool.

Agents never reference server names, transport types, or tool implementations.
They ask the gateway to execute a named capability and receive a ToolResult.

Architecture:

    Investigator
          │
          ▼
    ToolGateway
          │
    ┌─────┼─────────────┐
    │     │             │
    ▼     ▼             ▼
Knowledge  GitHub    Prometheus
  Server   Server      Server
    │         │           │
    ▼         ▼           ▼
Repository GitHub API  Prom API
    │
    ▼
 Filesystem
    │
 (later)
    ▼
 Postgres / Qdrant

Adding a new server requires:
  1. Implement BaseMCPServer
  2. Register with ServerRegistry at startup
  3. No changes to ToolGateway, agents, or any other code.
"""
import logging
from typing import Any, Dict, List, Optional

from ..registry.server_registry import ServerRegistry
from ..types import ToolResult, ToolDefinition

logger = logging.getLogger(__name__)


class ToolGateway:
    """Unified gateway for all MCP tool invocations.

    The Investigator (and any future agent) depends only on this class.
    It is injected via the DI container — agents never instantiate it directly.

    Usage:
        result = await self.tool_gateway.execute(
            server="knowledge",
            tool="search_documents",
            arguments={"query": "feature drift PSI"}
        )

        # Discover what tools are available across all servers
        tools = self.tool_gateway.discover_tools()
    """

    def __init__(self, registry: ServerRegistry) -> None:
        self._registry = registry

    # ------------------------------------------------------------------
    # Core execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        server: str,
        tool: str,
        arguments: Optional[Dict[str, Any]] = None,
    ) -> ToolResult:
        """Execute a namespaced tool and return a structured ToolResult.

        Args:
            server:    Target server namespace ('knowledge', 'github', etc.)
            tool:      Tool name within that server.
            arguments: Tool arguments. Defaults to empty dict.

        Returns:
            ToolResult — always structured, never raises.
        """
        logger.debug("[ToolGateway] execute(server=%r, tool=%r)", server, tool)
        return await self._registry.execute(server, tool, arguments or {})

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    async def discover_tools(self) -> List[ToolDefinition]:
        """Return all ToolDefinitions across every registered server.

        Agents can call this to dynamically inspect what capabilities
        are available — enabling future LLM-driven tool selection.
        """
        return await self._registry.list_tools()


    def list_servers(self) -> List[str]:
        """Return the names of all registered servers."""
        return self._registry.list_servers()

    def __repr__(self) -> str:
        servers = self._registry.list_servers()
        return f"<ToolGateway servers={servers}>"
