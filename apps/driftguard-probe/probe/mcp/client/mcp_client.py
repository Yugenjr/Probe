"""MCP client protocol and in-process implementation.

The MCPClientProtocol defines the interface any client must satisfy.
InProcessMCPClient is the concrete implementation for local servers.
Future implementations: HttpMCPClient, StdioMCPClient.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict

from ..server import BaseMCPServer
from ..types import ToolResult


class MCPClientProtocol(ABC):
    """Abstract protocol for MCP client implementations.

    All clients — in-process, HTTP, stdio — satisfy this interface,
    keeping the rest of the stack transport-agnostic.
    """

    @abstractmethod
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Invoke a named tool on the connected MCP server."""
        ...

    @property
    @abstractmethod
    def server_name(self) -> str:
        """Name of the server this client is connected to."""
        ...


class InProcessMCPClient(MCPClientProtocol):
    """Concrete MCP client that calls a BaseMCPServer in the same process.

    Used when the server lives in the same Python runtime (KnowledgeServer).
    For remote servers, use HttpMCPClient or StdioMCPClient.
    """

    def __init__(self, server: BaseMCPServer) -> None:
        self._server = server

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Invoke a tool directly on the wrapped server."""
        return await self._server.handle_tool_call(tool_name, arguments)

    @property
    def server_name(self) -> str:
        return self._server.name
