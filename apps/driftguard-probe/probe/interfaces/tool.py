"""Tool Provider protocol abstractions."""
from typing import Any, Dict, Protocol, runtime_checkable


@runtime_checkable
class ToolProvider(Protocol):
    """Abstract interface for agent functional capabilities and tools."""

    @property
    def name(self) -> str:
        """Unique functional tool identifier."""
        ...

    @property
    def description(self) -> str:
        """Natural language description for LLM planning consumption."""
        ...

    @property
    def input_schema(self) -> Dict[str, Any]:
        """JSON Schema representation of expected tool inputs."""
        ...

    async def invoke(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute functional logic via underlying adapter or computation."""
        ...
