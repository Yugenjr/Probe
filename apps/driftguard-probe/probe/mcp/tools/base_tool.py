"""BaseMCPTool — abstract base every tool must implement."""
from abc import ABC, abstractmethod
from typing import Any

from ..types import ToolResult, ToolDefinition


class BaseMCPTool(ABC):
    """Abstract base for every tool registered within an MCP server.

    A tool is a single, focused capability unit. It declares its parameter
    schema via ToolDefinition and executes logic returning a ToolResult.

    The tool is isolated from:
      - Transport concerns (how the request arrived)
      - Registry concerns (how it was discovered)
      - Agent concerns (who called it and why)
    """

    @property
    @abstractmethod
    def definition(self) -> ToolDefinition:
        """Tool metadata including name, description, and JSON Schema parameters.

        The registry aggregates these for discovery. The LLM can inspect them
        to decide which tools to invoke dynamically.
        """
        ...

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool's core logic.

        Arguments are passed as keyword arguments matching the definition's
        parameter schema. Always returns ToolResult — never raises.
        """
        ...
