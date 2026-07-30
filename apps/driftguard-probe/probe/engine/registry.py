"""AgentRegistry managing specialized agent class registration and lookup."""
import logging
from typing import Dict, Type, Optional
from ..agents.base import BaseAgent

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Registry maintaining mappings of role names to specialized Agent classes."""

    def __init__(self):
        self._agents: Dict[str, Type[BaseAgent]] = {}

    def register(self, role_name: str, agent_class: Type[BaseAgent]) -> None:
        """Register an agent class associated with a specific role name."""
        self._agents[role_name] = agent_class
        logger.debug("Registered agent class '%s' for role '%s'", agent_class.__name__, role_name)

    def get(self, role_name: str) -> Type[BaseAgent]:
        """Look up an agent class by its role name."""
        if role_name not in self._agents:
            raise KeyError(f"Agent '{role_name}' is not registered in the AgentRegistry.")
        return self._agents[role_name]


_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    """Acquire the global singleton instance of AgentRegistry."""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
        from ..agents.supervisor import SupervisorAgent
        from ..agents.planner import PlannerAgent
        from ..agents.investigator import InvestigatorAgent
        from ..agents.triage import TriageAgent
        from ..agents.memory import MemoryRecallAgent
        from ..agents.timeline import TimelineAnalystAgent
        from ..agents.metrics import MetricAnalystAgent
        from ..agents.repo import RepoAnalystAgent
        from ..agents.logs import LogForensicsAgent
        from ..agents.causal import CausalSynthesisAgent
        from ..agents.critic import AdversarialCriticAgent
        from ..agents.architect import InterventionArchitectAgent
        from ..agents.compliance import ComplianceAgent
        from ..agents.reporter import ReporterAgent

        _registry.register("Supervisor", SupervisorAgent)
        _registry.register("Planner", PlannerAgent)
        _registry.register("Investigator", InvestigatorAgent)
        _registry.register("Triage", TriageAgent)
        _registry.register("MemoryRecall", MemoryRecallAgent)
        _registry.register("TimelineAnalyst", TimelineAnalystAgent)
        _registry.register("MetricAnalyst", MetricAnalystAgent)
        _registry.register("RepoAnalyst", RepoAnalystAgent)
        _registry.register("LogForensics", LogForensicsAgent)
        _registry.register("CausalSynthesis", CausalSynthesisAgent)
        _registry.register("AdversarialCritic", AdversarialCriticAgent)
        _registry.register("InterventionArchitect", InterventionArchitectAgent)
        _registry.register("Compliance", ComplianceAgent)
        _registry.register("Reporter", ReporterAgent)
    return _registry
