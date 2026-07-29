"""InProcessTransport — calls a BaseMCPServer directly in the same Python process.

When external MCP servers are added (GitHub, Prometheus), an HttpTransport
or StdioTransport can be implemented with the same interface. The registry
and agents never see transport details.
"""
from typing import Any, Dict
import logging

from ..server import BaseMCPServer
from ..types import ToolResult

logger = logging.getLogger(__name__)


class InProcessTransport:
    """Synchronous in-process transport for local MCP servers.

    Calls the server's handle_tool_call() directly — no network, no serialization.
    This is the correct transport for servers that live in the same process:
      - KnowledgeServer (filesystem)
      - Any future in-process server

    For remote servers, implement HttpTransport or StdioTransport with the same
    ``call(tool_name, arguments) -> ToolResult`` interface.
    """

    def __init__(self, server: BaseMCPServer) -> None:
        self._server = server

    async def call(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Forward a tool call to the wrapped server."""
        logger.debug(
            "[InProcessTransport] → %s/%s args=%s",
            self._server.name, tool_name, list(arguments.keys())
        )
        return await self._server.handle_tool_call(tool_name, arguments)

    @property
    def server_name(self) -> str:
        return self._server.name
