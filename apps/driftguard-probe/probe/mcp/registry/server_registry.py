"""ServerRegistry — namespaced tool routing across multiple MCP servers.

Supports registering local (in-process) and remote (HTTP / process stdio) servers
behind a unified interface.
"""
import time
import logging
from typing import Dict, List, Optional, Union, Any

from ..server import BaseMCPServer
from ..transport.in_process import InProcessTransport
from ..types import ToolResult, ToolDefinition

logger = logging.getLogger(__name__)


class ServerRegistry:
    """Registry for local and remote MCP servers.

    Supports namespaced tool routing and dynamic capability discovery.
    """

    def __init__(self) -> None:
        self._servers: Dict[str, BaseMCPServer] = {}
        # Union[InProcessTransport, HttpTransport, ProcessTransport]
        self._transports: Dict[str, Any] = {}
        self._types: Dict[str, str] = {}  # server_name -> type ('local', 'http', 'process')

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        server_or_name: Union[BaseMCPServer, str],
        transport: Optional[Any] = None,
        server_type: str = "local"
    ) -> None:
        """Register a server with its transport.

        Args:
            server_or_name: BaseMCPServer instance for local, or name string for remote.
            transport: Concrete transport instance (optional for local).
            server_type: Type descriptor ('local', 'http', 'process').
        """
        if isinstance(server_or_name, BaseMCPServer):
            server = server_or_name
            name = server.name
            self._servers[name] = server
            self._transports[name] = InProcessTransport(server)
            self._types[name] = "local"
            tool_names = [t.name for t in server.get_tools()]
            logger.info(
                "[ServerRegistry] Registered local server='%s' tools=%s",
                name, tool_names
            )
        else:
            name = server_or_name
            if not transport:
                raise ValueError("Transport is required for remote server registration.")
            self._transports[name] = transport
            self._types[name] = server_type
            logger.info(
                "[ServerRegistry] Registered remote server='%s' type='%s'",
                name, server_type
            )

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def get_server(self, name: str) -> Optional[BaseMCPServer]:
        """Return a registered local server by name, or None."""
        return self._servers.get(name)

    def get_transport(self, name: str) -> Optional[Any]:
        """Return the transport registered for a server."""
        return self._transports.get(name)

    def get_server_type(self, name: str) -> str:
        """Return the transport type of the registered server."""
        return self._types.get(name, "unknown")

    def list_servers(self) -> List[str]:
        """Names of all registered servers."""
        return list(self._transports.keys())

    async def list_tools(self) -> List[ToolDefinition]:
        """All tool definitions across every registered server.

        Inspects local servers synchronously and queries remote transports
        concurrently with individual timeouts so one slow server never
        blocks the rest.
        """
        import asyncio

        definitions: List[ToolDefinition] = []

        # Collect local tools synchronously (in-process, always fast)
        remote_names = []
        for name in self._transports:
            if name in self._servers:
                definitions.extend(self._servers[name].get_tools())
            else:
                remote_names.append(name)

        if not remote_names:
            return definitions

        # Query all remote transports concurrently, each capped at 30 s
        async def _fetch(name: str) -> List[ToolDefinition]:
            transport = self._transports[name]
            if not hasattr(transport, "list_tools"):
                return []
            try:
                return await asyncio.wait_for(transport.list_tools(), timeout=180.0)
            except asyncio.TimeoutError:
                logger.warning("[ServerRegistry] list_tools timed out for '%s'", name)
                return []
            except asyncio.CancelledError:
                logger.warning("[ServerRegistry] list_tools cancelled for '%s'", name)
                return []
            except Exception as e:
                logger.error("[ServerRegistry] Failed listing tools for %s: %s", name, e)
                return []

        results = await asyncio.gather(*[_fetch(n) for n in remote_names])
        for tools in results:
            definitions.extend(tools)

        return definitions

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(
        self,
        server: str,
        tool: str,
        arguments: Optional[Dict] = None,
    ) -> ToolResult:
        """Execute a namespaced tool call.

        Args:
            server:    Target server name ('knowledge', 'github', etc.)
            tool:      Tool name within that server.
            arguments: Tool arguments.

        Returns:
            ToolResult — always. Never raises.
        """
        if arguments is None:
            arguments = {}

        transport = self._transports.get(server)
        if transport is None:
            msg = (
                f"No server registered with name '{server}'. "
                f"Registered servers: {self.list_servers()}"
            )
            logger.error("[ServerRegistry] %s", msg)
            return ToolResult(success=False, content="", error=msg)

        start = time.perf_counter()
        try:
            result = await transport.call(tool, arguments)
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            logger.debug(
                "[ServerRegistry] %s/%s → success=%s in %dms",
                server, tool, result.success, elapsed_ms
            )
            return result
        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            msg = f"Unhandled error from server '{server}' tool '{tool}': {e}"
            logger.error("[ServerRegistry] %s", msg, exc_info=True)
            return ToolResult(
                success=False,
                content="",
                error=msg,
                execution_time_ms=elapsed_ms,
            )

    def __repr__(self) -> str:
        return f"<ServerRegistry servers={self.list_servers()}>"
