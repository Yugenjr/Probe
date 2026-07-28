"""Remediation domain expert agent formulating engineering interventions and estimating impact."""
import logging
from typing import Any, Dict
from .base import BaseAgent
from ..engine.state import InvestigationSession
from ..domain.remediation import RemediationPlan, InterventionType
from ..tools.execution import EstimateRetrainingImpactTool
from ..core.di import get_container

logger = logging.getLogger(__name__)


class RemediationAgent(BaseAgent):
    """Actionable engineering intervention formulation and impact prediction expert.
    
    Simulates projected model accuracy recovery and prepares automated CI/CD retraining job dispatches,
    enforcing human executive sign-off interlocks where required by enterprise policy.
    """
    @property
    def role_name(self) -> str:
        return "Remediation Engineer"

    async def execute(self, state: InvestigationSession, **kwargs: Any) -> Dict[str, Any]:
        logger.info("Remediation Agent formulating intervention plan for session %s", state.session_id)
        container = getattr(self, "container", get_container())
        
        impact_tool = EstimateRetrainingImpactTool(container=container)
        impact = await impact_tool.invoke(model_id=state.incident.model_id)
        
        hyp_id = state.hypotheses[0].hypothesis_id if state.hypotheses else None
        plan = RemediationPlan(
            remediation_id=f"rem-{state.session_id[:8]}",
            target_model_id=state.incident.model_id,
            intervention_type=InterventionType.AUTOMATED_RETRAINING,
            summary="Dispatch automated retraining pipeline on latest 7-day demographic feature slice with adjusted alarm threshold.",
            execution_parameters={"slice_days": 7, "threshold_override": 0.10},
            supporting_hypothesis_id=hyp_id,
            estimated_impact_percent=float(impact.get("simulated_accuracy_recovery_percent", 14.8)),
            requires_human_approval=True,
        )
        state.attach_remediation(plan)
        
        return {"status": "REMEDIATION_PROPOSED", "remediation_id": plan.remediation_id, "impact_simulation": impact}


# Backwards compatible alias
ExperimenterAgent = RemediationAgent
