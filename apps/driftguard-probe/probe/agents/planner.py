"""Planner Agent mapping task dependency DAGs and resource timeline execution scheduling."""
import logging
from typing import Any, Dict, List
from .base import BaseAgent
from ..core.state import InvestigationState
from ..core.lifecycle import InvestigationStatus

logger = logging.getLogger(__name__)


import json
from pydantic import BaseModel, Field
from ..mcp.capability import EvidencePlan, CapabilityRequest

class InvestigationPlan(BaseModel):
    """Investigation plan schema detailing objectives, diagnostic questions, and evidence targets."""
    objectives: List[str] = Field(..., description="List of primary investigation objectives")
    questions: List[str] = Field(..., description="List of key diagnostic questions to resolve")
    evidence_plan: EvidencePlan = Field(..., description="The capability requests for retrieving evidence")


class PlannerAgent(BaseAgent):
    """Task Execution Graph & Timeline Scheduling Agent.
    
    Constructs an optimized Directed Acyclic Graph (DAG) of required diagnostic capabilities
    based on anomaly trigger types and calculates concurrency resource timeline estimates.
    """
    @property
    def role_name(self) -> str:
        return "Planner"

    async def execute(self, state: InvestigationState, **kwargs: Any) -> Dict[str, Any]:
        logger.info("Planner Agent generating execution plan for incident: %s", state.incident.incident_id)
        
        # Static fallback plan definition using capabilities
        fallback_plan = {
            "status": "PLAN_GENERATED",
            "objectives": ["Identify feature drift root cause", "Verify model latency correlation"],
            "questions": ["Is feature drift causing latency surge?", "Is demographic shift the root cause?"],
            "evidence_plan": {
                "goal": "Determine feature drift and performance root cause",
                "capabilities": [
                    {"capability": "runbooks", "priority": 1, "required": True, "status": "pending"},
                    {"capability": "experiment_traces", "priority": 2, "required": True, "status": "pending"},
                    {"capability": "code_history", "priority": 3, "required": False, "status": "pending"}
                ]
            }
        }
        
        if self.llm_provider and hasattr(self.llm_provider, "generate_step_structured"):
            # 1. Compile context dictionary
            context_data = {}
            if state.investigation_context:
                context_data["context"] = state.investigation_context.model_dump(mode="json")
            else:
                context_data["incident"] = state.incident.model_dump(mode="json")

            context_json = json.dumps(context_data, indent=2)

            try:
                # 2. Call structured step generation
                plan = await self.llm_provider.generate_step_structured(
                    prompt_name="planner",
                    prompt_version="v1",
                    response_model=InvestigationPlan,
                    context={"context_json": context_json},
                    temperature=0.1
                )
                logger.info("Planner Agent successfully generated plan via LLM.")
                
                # 3. Save evidence plan to session state for downstream agents
                state.evidence_plan = plan.evidence_plan
                
                # 4. Update execution history and return JSON payload
                state.execution_history.append(
                    f"[Planner] Generated InvestigationPlan (LLM) with {len(plan.evidence_plan.capabilities)} capabilities."
                )
                result = plan.model_dump(mode="json")
                result["status"] = "PLAN_GENERATED"
                return result
            except Exception as e:
                logger.warning("LLM generation failed in PlannerAgent, falling back to static plan: %s", e)

        # Fallback to static plan if no LLM provider or generation fails
        static_evidence_plan = EvidencePlan(**fallback_plan["evidence_plan"])
        state.evidence_plan = static_evidence_plan
        state.execution_history.append(
            f"[Planner] Generated InvestigationPlan (Fallback) with capabilities: {[c.capability for c in static_evidence_plan.capabilities]}"
        )
        return fallback_plan


