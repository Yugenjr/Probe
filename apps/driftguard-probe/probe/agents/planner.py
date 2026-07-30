"""Planner Agent mapping task dependency DAGs and resource timeline execution scheduling."""
import logging
from typing import Any, Dict, List
from .base import BaseAgent
from ..core.state import InvestigationState
from ..core.lifecycle import InvestigationStatus

logger = logging.getLogger(__name__)


import json
from pydantic import BaseModel, Field

class InvestigationPlan(BaseModel):
    """Investigation plan schema detailing objectives, diagnostic questions, and evidence targets."""
    objectives: List[str] = Field(..., description="List of primary investigation objectives")
    questions: List[str] = Field(..., description="List of key diagnostic questions to resolve")
    evidence_requirements: List[str] = Field(default_factory=list, description="General evidence types required, without specifying specific tools")


class PlannerAgent(BaseAgent):
    """Strategic investigation architect.
    
    Constructs an optimized Directed Acyclic Graph (DAG) of required diagnostic questions
    based on anomaly trigger types.
    """
    @property
    def role_name(self) -> str:
        return "Planner"

    async def execute(self, state: InvestigationState, **kwargs: Any) -> Dict[str, Any]:
        logger.info("Planner Agent generating execution plan for incident: %s", state.incident.incident_id)
        
        fallback_plan = {
            "status": "PLAN_GENERATED",
            "objectives": ["Identify feature drift root cause", "Verify model latency correlation"],
            "questions": ["Is feature drift causing latency surge?", "Is demographic shift the root cause?"],
            "evidence_requirements": ["runbooks", "experiment_traces", "code_history"]
        }
        
        if self.llm_provider and hasattr(self.llm_provider, "generate_step_structured"):
            # 1. Compile context dictionary
            context_data = {}
            if state.investigation_context:
                context_data["context"] = state.investigation_context.model_dump(mode="json")
            else:
                context_data["incident"] = state.incident.model_dump(mode="json")

            context_json = json.dumps(context_data, indent=2)
            if len(context_json) > 12000:
                context_json = context_json[:12000] + "\n...[TRUNCATED]"

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
                
                # 3. Update execution history and return JSON payload
                state.execution_history.append(
                    f"[Planner] Generated InvestigationPlan (LLM) with {len(plan.questions)} diagnostic questions."
                )
                result = plan.model_dump(mode="json")
                result["status"] = "PLAN_GENERATED"
                return result
            except Exception as e:
                logger.warning("LLM generation failed in PlannerAgent, falling back to static plan: %s", e)

        # Fallback to static plan if no LLM provider or generation fails
        state.execution_history.append(
            f"[Planner] Generated InvestigationPlan (Fallback) with questions: {fallback_plan['questions']}"
        )
        return fallback_plan



