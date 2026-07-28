"""Abstract Base Agent definition."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from ..core.state import InvestigationState
from ..interfaces.llm import LLMProvider
from ..interfaces.tool import ToolProvider


class BaseAgent(ABC):
    """Abstract base class for every autonomous reasoning agent in Probe.
    
    Enforces a strict architectural rule: agents never make direct HTTP calls or import external
    repositories. They communicate purely via Pydantic v2 schemas and execute capabilities via Tools.
    """
    def __init__(self, llm_provider: Optional[LLMProvider] = None, tools: Optional[List[ToolProvider]] = None):
        self.llm_provider = llm_provider
        self.tools = {t.name: t for t in (tools or [])}

    @property
    @abstractmethod
    def role_name(self) -> str:
        """Unique specialized identifier e.g., 'Investigator' or 'Hypothesis'."""
        pass

    @abstractmethod
    async def execute(self, state: InvestigationState, **kwargs: Any) -> Any:
        """Execute single specialized domain responsibility against active investigation state."""
        pass

    async def invoke_tool(self, tool_name: str, **kwargs: Any) -> Dict[str, Any]:
        """Safely invoke an assigned tool capability."""
        if tool_name not in self.tools:
            raise KeyError(f"Tool '{tool_name}' is not assigned to agent '{self.role_name}'.")
        return await self.tools[tool_name].invoke(**kwargs)
