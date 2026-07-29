"""Unit tests for ServerRegistry and ToolGateway MCP components."""
import pytest
from typing import Any, Dict, List

from probe.mcp.server import BaseMCPServer
from probe.mcp.types import ToolResult, ToolDefinition
from probe.mcp.registry.server_registry import ServerRegistry
from probe.mcp.gateway.tool_gateway import ToolGateway


class MockSimpleServer(BaseMCPServer):
    """Simple mock server to verify registry routing and execution mapping."""

    @property
    def name(self) -> str:
        return "mock_simple"

    def get_tools(self) -> List[ToolDefinition]:
        return [
            ToolDefinition(
                name="hello",
                description="Greets the user",
                parameters={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "default": "world"}
                    }
                },
                server="mock_simple"
            )
        ]

    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        if tool_name == "hello":
            name = arguments.get("name", "world")
            return ToolResult(
                success=True,
                content=f"Hello, {name}!",
                metadata={"sender": "mock_simple"}
            )
        return ToolResult(success=False, content="", error=f"Unknown tool: {tool_name}")


@pytest.mark.anyio
async def test_registry_registration_and_execution():
    """Verify registry registers servers and executes namespaced tools successfully."""
    registry = ServerRegistry()
    server = MockSimpleServer()
    registry.register(server)

    # Verify discovery
    assert registry.list_servers() == ["mock_simple"]
    tools = await registry.list_tools()
    assert len(tools) == 1
    assert tools[0].name == "hello"
    assert tools[0].qualified_name == "mock_simple.hello"

    # Verify tool execution
    res = await registry.execute("mock_simple", "hello", {"name": "Antigravity"})
    assert res.success is True
    assert res.content == "Hello, Antigravity!"
    assert res.metadata["sender"] == "mock_simple"

    # Verify missing server graceful failure
    res_fail = await registry.execute("unknown_server", "hello", {})
    assert res_fail.success is False
    assert "No server registered" in res_fail.error


@pytest.mark.anyio
async def test_tool_gateway_delegation():
    """Verify ToolGateway delegates discovery and execution correctly to registry."""
    registry = ServerRegistry()
    server = MockSimpleServer()
    registry.register(server)
    gateway = ToolGateway(registry=registry)

    assert gateway.list_servers() == ["mock_simple"]
    assert len(await gateway.discover_tools()) == 1

    res = await gateway.execute("mock_simple", "hello", {"name": "Agent"})
    assert res.success is True
    assert res.content == "Hello, Agent!"

