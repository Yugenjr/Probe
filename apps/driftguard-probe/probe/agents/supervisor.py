"""Supervisor Agent selecting domain workflows."""
import logging
from typing import Any
from .base import BaseAgent
from ..core.state import InvestigationState
from ..workflows.investigation import DriftInvestigationWorkflow

logger = logging.getLogger(__name__)


class SupervisorAgent(BaseAgent):
    """Supervisor agent managing incident routing to high-level domain workflows.
    
    The supervisor does NOT manually invoke low-level reasoning steps. It selects an
    appropriate workflow (Drift, Retraining, Compliance) and oversees progression.
    """
    @property
    def role_name(self) -> str:
        return "Supervisor"

    async def execute(self, state: InvestigationState, **kwargs: Any) -> InvestigationState:
        logger.info("Supervisor Agent examining incident %s", state.incident.incident_id)
        # Choose default DriftInvestigationWorkflow for baseline incidents
        workflow = DriftInvestigationWorkflow()
        logger.debug("Supervisor selected workflow: %s", workflow.name)
        return await workflow.execute(state)
        # TODO: Implementation pending for LLM-assisted multi-workflow selection logic
