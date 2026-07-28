"""Intervention Architect cognitive reasoning agent formulating actionable engineering remediation strategies."""
import logging
from typing import Any, Dict
from .base import BaseAgent
from ..engine.state import InvestigationSession
from ..domain.remediation import RemediationPlan, InterventionType
from ..tools.execution import EstimateRetrainingImpactTool
from ..core.di import get_container

logger = logging.getLogger(__name__)


class InterventionArchitectAgent(BaseAgent):
    """Actionable engineering intervention design and accuracy impact projection architect.
    
    Designs safe automated retraining CI/CD dispatches and enforces enterprise human review interlocks
    whenever high-impact modifications threaten production SLA boundaries.
    """
    @property
    def role_name(self) -> str:
        return "Intervention Architect"

    async def execute(self, state: InvestigationSession, **kwargs: Any) -> Dict[str, Any]:
        logger.info("InterventionArchitectAgent designing remediation strategy for %s", state.session_id)
        container = getattr(self, "container", get_container())
        
        impact_tool = EstimateRetrainingImpactTool(container=container)
        impact = await impact_tool.invoke(model_id=state.incident.model_id)
        
        hyp_id = state.hypotheses[0].hypothesis_id if state.hypotheses else None
        plan = RemediationPlan(
            remediation_id=f"arch-{state.session_id[:8]}",
            target_model_id=state.incident.model_id,
            intervention_type=InterventionType.AUTOMATED_RETRAINING,
            summary="Dispatch automated retraining pipeline with dynamic Covariate Slice filtering and updated alerting threshold.",
            execution_parameters={"slice_days": 7, "threshold_override": 0.12},
            supporting_hypothesis_id=hyp_id,
            estimated_impact_percent=float(impact.get("simulated_accuracy_recovery_percent", 15.2)),
            requires_human_approval=True,
        )
        state.attach_remediation(plan)
        
        return {"status": "REMEDIATION_DESIGNED", "remediation_id": plan.remediation_id, "impact_projection": impact}
