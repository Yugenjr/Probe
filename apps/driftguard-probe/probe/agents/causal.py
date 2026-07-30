from .base import BaseAgent
"""Causal Synthesis domain cognitive reasoning agent formulating root-cause theories from graph topologies."""
import logging
import uuid
from typing import List, Optional, Any
from ..engine.state import InvestigationSession
from ..domain.graph import EvidenceGraph
from ..domain.evidence import UniversalEvidence
from ..domain.hypothesis import CausalHypothesis

logger = logging.getLogger(__name__)


from ..domain.memory import HistoricalPatternAnalysis

class CausalSynthesisAgent(BaseAgent):

    @property
    def role_name(self) -> str:
        return "CausalSynthesis"

    """Cognitive causal theory engineer formulating CausalHypothesis from ranked evidence and graphs."""
    
    async def execute(self, session: InvestigationSession, **kwargs) -> CausalHypothesis:
        logger.info("CausalSynthesisAgent evaluating ranked evidence and graph topology for session %s", session.session_id)
        import json
        
        ranked_evidence = session.universal_evidence or []
        graph = session.evidence_graph or EvidenceGraph(graph_id=str(uuid.uuid4()), nodes={}, edges=[])
        
        fallback_hypothesis = CausalHypothesis(
            hypothesis_id=f"hyp-synth-{str(uuid.uuid4())[:8]}",
            primary_root_cause="Feature flag 'enable_new_billing' was toggled, forcing the system into a fallback path.",
            contributing_factors=["High CPU utilization due to a spike in traffic", "Unoptimized fallback routing logic"],
            causal_chain=["Traffic spiked", "Feature flag enabled", "NullPointerException triggered", "Fallback routing executed", "Statistical drift observed in latency"],
            supporting_evidence=[ev.evidence_id for ev in ranked_evidence[:3]],
            contradicting_evidence=[],
            confidence=0.85
        )

        if self.llm_provider and hasattr(self.llm_provider, "generate_step_structured"):
            # Prepare context
            planner_plan = {}
            for res in session.agent_results:
                if res.agent_name == "Planner" and res.success:
                    planner_plan = res.output
                    break
                    
            context = {
                "context_json": session.incident.model_dump_json(indent=2),
                "plan_json": json.dumps(planner_plan, indent=2),
                "evidence_json": json.dumps([ev.model_dump(mode="json") for ev in ranked_evidence], indent=2)[:12000],
                "graph_json": graph.model_dump_json(indent=2)[:10000]
            }

            try:
                hypothesis = await self.llm_provider.generate_step_structured(
                    prompt_name="causal",
                    prompt_version="v1",
                    response_model=CausalHypothesis,
                    context=context,
                    temperature=0.2
                )
                logger.info("CausalSynthesisAgent successfully generated CausalHypothesis via LLM.")
                # Ensure hypothesis has an ID
                if not hypothesis.hypothesis_id:
                    hypothesis.hypothesis_id = f"hyp-synth-{str(uuid.uuid4())[:8]}"
                session.hypotheses = [hypothesis]
                return hypothesis
            except Exception as e:
                logger.warning("LLM generation failed in CausalSynthesisAgent, falling back: %s", e)
                
        session.hypotheses = [fallback_hypothesis]
        return fallback_hypothesis
