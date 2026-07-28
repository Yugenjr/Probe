"""Dynamic agent capability registry."""
import logging
from typing import Dict, List, Type, Any
from ...agents.base import BaseAgent

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Registry allowing pluggable autonomous agent discovery and instantiation."""
    def __init__(self):
        self._agents: Dict[str, Type[BaseAgent]] = {}

    def register(self, agent_name: str, agent_class: Type[BaseAgent]) -> None:
        """Register a new specialized reasoning agent or plugin agent."""
        if agent_name in self._agents:
            logger.warning("Agent %s already registered. Overwriting.", agent_name)
        self._agents[agent_name] = agent_class
        logger.debug("Registered agent: %s", agent_name)

    def get(self, agent_name: str, **kwargs: Any) -> BaseAgent:
        """Instantiate and return a registered agent class."""
        if agent_name not in self._agents:
            raise KeyError(f"Agent '{agent_name}' is not registered.")
        return self._agents[agent_name](**kwargs)

    def discover(self) -> List[str]:
        """Return a list of all registered agent identifiers."""
        return list(self._agents.keys())

    # TODO: Implementation pending for automatic entry_point dynamic discovery via plugins


_global_agent_registry = AgentRegistry()


def get_agent_registry() -> AgentRegistry:
    """Acquire singleton agent registry instance."""
    return _global_agent_registry
