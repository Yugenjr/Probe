"""MCP tool dispatch bridging JSON-RPC calls to ToolRegistry."""
import logging
from typing import Any, Dict
from ...core.registry.tool_registry import get_tool_registry

logger = logging.getLogger(__name__)


async def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Bridge incoming MCP RPC call to internal tool registry execution."""
    registry = get_tool_registry()
    logger.debug("Dispatching MCP Tool Call to: %s", tool_name)
    return await registry.invoke(tool_name, **arguments)
