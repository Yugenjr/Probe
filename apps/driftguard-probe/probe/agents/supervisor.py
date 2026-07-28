"""Supervisor Agent selecting domain workflows."""
import logging
from typing import Any
from .base import BaseAgent
from ..engine.state import InvestigationSession
from ..engine.workflow import ExecutionPlan, ExecutionStep

logger = logging.getLogger(__name__)


class SupervisorAgent(BaseAgent):
    """Supervisor agent managing incident routing and generating the sequential ExecutionPlan.
    
    The supervisor does NOT run the individual reasoning steps; it coordinates the plan layout.
    """
    @property
    def role_name(self) -> str:
        return "Supervisor"

    async def execute(self, state: InvestigationSession, **kwargs: Any) -> ExecutionPlan:
        logger.info("Supervisor Agent examining incident %s", state.incident.incident_id)
        
        plan = ExecutionPlan(
            steps=[
                ExecutionStep(agent_role="Planner", description="Establish investigation scope and objectives"),
                ExecutionStep(agent_role="Investigator", description="Ingest and analyze telemetry data anomalies"),
                ExecutionStep(agent_role="Hypothesis", description="Formulate causal root-cause theories from evidence"),
                ExecutionStep(agent_role="Evaluator", description="Evaluate hypotheses and recommend optimal intervention"),
                ExecutionStep(agent_role="Reporter", description="Synthesize findings and compile forensic report")
            ]
        )
        logger.info("Supervisor generated execution plan with %d steps.", len(plan.steps))
        state.execution_history.append(
            f"[Supervisor] Supervisor generated execution plan with {len(plan.steps)} steps."
        )
        return plan
