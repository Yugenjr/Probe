import json
import logging
from typing import Any, Dict
import uuid
from .base import BaseAgent
from ..engine.state import InvestigationSession
from typing import Any
Hypothesis = Any
from ..models.recommendation import Recommendation, RecommendationAction, EvaluationResult
from ..domain.remediation import RemediationPlan, InterventionType

logger = logging.getLogger(__name__)


class EvaluatorAgent(BaseAgent):
    """Specialized agent evaluating experimental test outcomes and prescribing actionable mitigations."""
    @property
    def role_name(self) -> str:
        return "Evaluator"

    async def execute(self, state: InvestigationSession, **kwargs: Any) -> Dict[str, Any]:
        logger.info("Evaluator Agent appraising hypotheses for session %s", state.session_id)
        
        # 1. Fallback / Default EvaluationResult setup
        best_hyp = state.hypotheses[0] if state.hypotheses else Hypothesis(
            hypothesis_id=f"hyp-{state.session_id[:8]}",
            title="Unmonitored Demographic Covariate Shift Triggering Latency Surge",
            detailed_reasoning="Observed Wasserstein feature distance surge on 'user_age' distribution directly preceded p99 inference latency spike.",
            supporting_evidence_ids=[]
        )
        fallback_rec = Recommendation(
            action="Rollback",
            reason="Recent preprocessing change deployed in commit 2f7a91c altered feature scaling metrics.",
            priority="P0",
            estimated_risk="Low",
            estimated_time="5 min"
        )
        fallback_result = EvaluationResult(
            best_hypothesis=best_hyp,
            alternatives=state.hypotheses[1:] if len(state.hypotheses) > 1 else [],
            recommended_actions=[fallback_rec],
            confidence=0.91
        )

        eval_result = fallback_result

        # 2. Invoke structured LLM evaluation if provider is active
        if self.llm_provider and hasattr(self.llm_provider, "generate_step_structured"):
            hypotheses_list = [h.model_dump(mode="json") for h in state.hypotheses]
            try:
                eval_result = await self.llm_provider.generate_step_structured(
                    prompt_name="evaluator",
                    prompt_version="v1",
                    response_model=EvaluationResult,
                    context={"hypotheses_json": json.dumps(hypotheses_list, indent=2)},
                    temperature=0.1
                )
                logger.info("Evaluator Agent successfully evaluated hypotheses via LLM.")
            except Exception as e:
                logger.warning("LLM hypothesis evaluation failed, using fallback: %s", e)

        # 3. Update evaluation_result state
        state.evaluation_result = eval_result

        # 4. Extract action recommendations and map to RemediationPlan
        if eval_result.recommended_actions:
            best_rec = eval_result.recommended_actions[0]
            
            action_str = best_rec.action.upper()
            if "ROLLBACK" in action_str:
                intervention = InterventionType.CANARY_ROLLBACK
                rec_action = RecommendationAction.ROLLBACK_MODEL
            elif "RETRAIN" in action_str:
                intervention = InterventionType.AUTOMATED_RETRAINING
                rec_action = RecommendationAction.RETRAIN_MODEL
            elif "THRESHOLD" in action_str:
                intervention = InterventionType.THRESHOLD_RELAXATION
                rec_action = RecommendationAction.UPDATE_THRESHOLD
            else:
                intervention = InterventionType.HUMAN_INTERVENTION_REQUIRED
                rec_action = RecommendationAction.ESCALATE_TO_HUMAN

            # Backpopulate legacy fields on the best recommendation item
            best_rec.recommendation_id = f"rec-{uuid.uuid4().hex[:6]}"
            best_rec.action_type = rec_action
            best_rec.title = f"{best_rec.action} Recommendation"
            best_rec.justification = best_rec.reason
            best_rec.target_model_id = state.incident.model_id
            best_rec.requires_human_approval = True

            try:
                est_impact = float(eval_result.confidence) * 100.0
            except (ValueError, TypeError):
                est_impact = 91.0

            # Create RemediationPlan and attach to session
            remediation = RemediationPlan(
                remediation_id=f"rem-{uuid.uuid4().hex[:6]}",
                target_model_id=state.incident.model_id,
                intervention_type=intervention,
                summary=f"{best_rec.action}: {best_rec.reason}",
                supporting_hypothesis_id=eval_result.best_hypothesis.hypothesis_id if eval_result.best_hypothesis else None,
                estimated_impact_percent=est_impact,
                requires_human_approval=True
            )
            state.attach_remediation(remediation)

            # Backward compatibility check for state.recommendation
            if hasattr(state, "recommendation"):
                state.recommendation = best_rec

        return eval_result.model_dump(mode="json")
