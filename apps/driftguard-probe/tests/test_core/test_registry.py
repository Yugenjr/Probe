"""Unit tests for dynamic agent and tool registry discoverability."""
import asyncio
import pytest
from typing import Any
from probe.core.registry.agent_registry import AgentRegistry
from probe.core.registry.tool_registry import ToolRegistry
from probe.agents.base import BaseAgent
from probe.tools.base import BaseTool


class DummyTestAgent(BaseAgent):
    @property
    def role_name(self) -> str:
        return "DummyTest"
    async def execute(self, state, **kwargs: Any) -> Any:
        return "OK"


class DummyTestTool(BaseTool):
    @property
    def name(self) -> str:
        return "dummy_tool"
    @property
    def description(self) -> str:
        return "Dummy description"
    @property
    def input_schema(self) -> dict:
        return {"type": "object"}
    async def invoke(self, **kwargs: Any) -> dict:
        return {"status": "SUCCESS"}


def test_agent_registry_operations():
    registry = AgentRegistry()
    registry.register("dummy", DummyTestAgent)
    assert "dummy" in registry.discover()
    agent = registry.get("dummy")
    assert agent.role_name == "DummyTest"


def test_tool_registry_operations():
    registry = ToolRegistry()
    tool = DummyTestTool()
    registry.register(tool)
    tools = registry.discover()
    assert len(tools) == 1
    assert tools[0]["name"] == "dummy_tool"

    res = asyncio.run(registry.invoke("dummy_tool"))
    assert res["status"] == "SUCCESS"
