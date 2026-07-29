"""ToolExecutor — timing and exception safety wrapper for tool invocation."""
import time
import logging
from typing import Any, Dict

from .base_tool import BaseMCPTool
from ..types import ToolResult

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Runs a BaseMCPTool with consistent timing measurement and exception handling.

    The server delegates actual invocation here so that every tool — regardless
    of server — gets the same error containment and observability treatment.
    """

    async def run(self, tool: BaseMCPTool, arguments: Dict[str, Any]) -> ToolResult:
        """Execute a tool, measure duration, catch all exceptions.

        Never raises. On failure, returns ToolResult(success=False, error=...).
        """
        tool_name = tool.definition.name
        start = time.perf_counter()

        try:
            result = await tool.execute(**arguments)
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            # Inject timing if not already set by the tool itself
            result.execution_time_ms = elapsed_ms
            logger.debug(
                "[ToolExecutor] %s completed in %dms | success=%s",
                tool_name, elapsed_ms, result.success
            )
            return result

        except TypeError as e:
            # Argument mismatch — likely a bad arguments dict
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            logger.warning("[ToolExecutor] %s argument error: %s", tool_name, e)
            return ToolResult(
                success=False,
                content="",
                error=f"Invalid arguments for tool '{tool_name}': {e}",
                execution_time_ms=elapsed_ms,
            )

        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            logger.error("[ToolExecutor] %s raised: %s", tool_name, e, exc_info=True)
            return ToolResult(
                success=False,
                content="",
                error=str(e),
                execution_time_ms=elapsed_ms,
            )
