"""Dynamic tool capability registry."""
import logging
from typing import Any, Dict, List, Optional
from ...interfaces.tool import ToolProvider

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry managing investigation Tools, exposing uniform register, discover, and invoke endpoints.
    
    Eventually, MCP servers simply query this registry to expose native tool bindings.
    """
    def __init__(self):
        self._tools: Dict[str, ToolProvider] = {}

    def register(self, tool: ToolProvider) -> None:
        """Register a functional tool provider instance."""
        if tool.name in self._tools:
            logger.warning("Tool %s already registered. Overwriting.", tool.name)
        self._tools[tool.name] = tool
        logger.debug("Registered tool: %s", tool.name)

    def discover(self) -> List[Dict[str, Any]]:
        """Return structured metadata and JSON input schemas for all available tools."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_schema,
            }
            for t in self._tools.values()
        ]

    async def invoke(self, tool_name: str, **kwargs: Any) -> Dict[str, Any]:
        """Locate and invoke a tool with provided arguments."""
        if tool_name not in self._tools:
            raise KeyError(f"Tool '{tool_name}' not found in ToolRegistry.")
        logger.info("Invoking tool '%s' via registry.", tool_name)
        return await self._tools[tool_name].invoke(**kwargs)

    # TODO: Implementation pending for parameter schema validation prior to invoke call


_global_tool_registry = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    """Acquire singleton tool registry instance."""
    return _global_tool_registry
