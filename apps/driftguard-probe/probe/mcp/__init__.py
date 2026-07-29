"""MCP infrastructure — public API surface.

The full MCP stack in four imports:

    from probe.mcp import ServerRegistry, ToolGateway, KnowledgeServer, ToolResult

Wiring a new investigation pipeline:
    registry = ServerRegistry()
    registry.register(KnowledgeServer())
    gateway = ToolGateway(registry)
    # Inject gateway into agents via DI container
"""
from .types import ToolResult, ToolDefinition, ToolRequest
from .server import BaseMCPServer
from .registry.server_registry import ServerRegistry
from .gateway.tool_gateway import ToolGateway
from .servers.knowledge.server import KnowledgeServer
from .bootstrap import bootstrap_mcp_registry

__all__ = [
    # Types
    "ToolResult",
    "ToolDefinition",
    "ToolRequest",
    # Abstractions
    "BaseMCPServer",
    # Infrastructure
    "ServerRegistry",
    "ToolGateway",
    # Servers
    "KnowledgeServer",
    # Boostrap
    "bootstrap_mcp_registry",
]

