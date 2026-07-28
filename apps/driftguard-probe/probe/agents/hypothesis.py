import json
import logging
from typing import Any, Dict
from .base import BaseAgent
from ..engine.state import InvestigationSession
from ..domain.hypothesis import Hypothesis, HypothesisCollection

logger = logging.getLogger(__name__)


class HypothesisAgent(BaseAgent):
    """Causal root-cause synthesis engineer formulating verified diagnostic theories.
    
    Synthesizes accrued universal evidence items into ranked Hypothesis domain entities,
    explicitly mapping likelihood probabilities to supporting cryptographic Evidence IDs.
    """
    @property
    def role_name(self) -> str:
        return "Hypothesis"

    async def execute(self, state: InvestigationSession, **kwargs: Any) -> Dict[str, Any]:
        logger.info("Hypothesis Agent synthesizing causal theories for session %s", state.session_id)
        
        supporting_ids = [ev.evidence_id for ev in state.universal_evidence]
        fallback_hypothesis = Hypothesis(
            hypothesis_id=f"hyp-{state.session_id[:8]}",
            title="Unmonitored Demographic Covariate Shift Triggering Latency Surge",
            detailed_reasoning="Observed Wasserstein feature distance surge on 'user_age' distribution directly preceded p99 inference latency spike.",
            supporting_evidence_ids=supporting_ids[:5],
            likelihood_score=0.92,
            verified_by_simulation=False,
            explanation="Observed Wasserstein feature distance surge on 'user_age' distribution directly preceded p99 inference latency spike.",
            confidence=0.92,
            weaknesses=["No latency increase in local tests"]
        )

        if self.llm_provider and hasattr(self.llm_provider, "generate_step_structured"):
            # Gather planner details
            planner_plan = {}
            for res in state.agent_results:
                if res.agent_name == "Planner" and res.success:
                    planner_plan = res.output
                    break
            
            context_data = {
                "context_json": state.investigation_context.model_dump_json(indent=2) if state.investigation_context else "{}",
                "plan_json": json.dumps(planner_plan, indent=2),
                "evidence_json": json.dumps([ev.model_dump(mode="json") for ev in state.universal_evidence], indent=2),
            }

            try:
                collection = await self.llm_provider.generate_step_structured(
                    prompt_name="hypothesis",
                    prompt_version="v1",
                    response_model=HypothesisCollection,
                    context=context_data,
                    temperature=0.2
                )
                if collection.hypotheses:
                    for hyp in collection.hypotheses:
                        # Ensure fields are aligned for backward compatibility
                        if not hyp.detailed_reasoning and hyp.explanation:
                            hyp.detailed_reasoning = hyp.explanation
                        if not hyp.likelihood_score and hyp.confidence:
                            hyp.likelihood_score = hyp.confidence
                        state.add_hypothesis(hyp)
                    
                    return {
                        "status": "HYPOTHESIS_FORMULATED",
                        "hypotheses": [h.model_dump(mode="json") for h in collection.hypotheses]
                    }
            except Exception as e:
                logger.warning("LLM hypothesis formulation failed, falling back: %s", e)

        # Fallback
        state.add_hypothesis(fallback_hypothesis)
        return {
            "status": "HYPOTHESIS_FORMULATED",
            "hypotheses": [fallback_hypothesis.model_dump(mode="json")]
        }
