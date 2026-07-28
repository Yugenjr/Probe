"""Abstract base tool class for agent analytical capabilities."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ..interfaces.tool import ToolProvider
from ..core.di import Container, get_container


class BaseTool(ABC, ToolProvider):
    """Abstract class enforcing functional execution contracts across investigation capabilities.
    
    Tools wrap abstract platform providers or local computational algorithms, guaranteeing
    that calling agents never communicate directly with concrete HTTP clients or DB connectors.
    """
    def __init__(self, container: Optional[Container] = None):
        self._container = container

    @property
    def container(self) -> Container:
        """Resolve Inversion of Control DI container at runtime."""
        return self._container or get_container()

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier string for tool registry lookup."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Natural language instruction guiding LLM planning behavior."""
        pass

    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """JSON schema defining expected parameter keys and typing."""
        pass

    @abstractmethod
    async def invoke(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute analytical capability and return structured dictionary."""
        pass
