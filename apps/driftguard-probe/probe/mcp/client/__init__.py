"""MCP client abstractions."""
from .mcp_client import MCPClientProtocol, InProcessMCPClient

__all__ = ["MCPClientProtocol", "InProcessMCPClient"]
