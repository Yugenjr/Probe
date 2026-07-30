"""Supervisor Agent selecting domain workflows and controlling the investigation execution loop."""
import logging
import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .base import BaseAgent
from ..engine.state import InvestigationSession, InvestigationStatus

logger = logging.getLogger(__name__)

class SupervisorCommand(BaseModel):
    """Rigorous control-flow command dispatched by the Supervisor."""
    action: str = Field(..., description="Action to take: NEXT_STAGE, LOOP_BACK, ESCALATE, TERMINATE")
    next_stage: Optional[InvestigationStatus] = Field(None, description="The specific stage to transition to, if action is NEXT_STAGE or LOOP_BACK")
    rationale: str = Field(..., description="Why this decision was made")
    request_reason: Optional[str] = Field(None, description="Optional precise reason for requesting a loop back or specific agents")
    required_agents: List[str] = Field(default_factory=list, description="Specific agents required in the next stage")
    missing_information: List[str] = Field(default_factory=list, description="Missing evidence required to proceed")
    confidence: float = Field(..., description="Confidence in the current investigation state (0.0 to 1.0)")
    terminate: bool = Field(False, description="Whether to end the investigation immediately")
    requires_human: bool = Field(False, description="Whether human intervention is required before proceeding")

class SupervisorAgent(BaseAgent):
    """Dynamic investigation commander evaluating state and delegating by stage."""
    
    @property
    def role_name(self) -> str:
        return "Supervisor"

    async def execute(self, state: InvestigationSession, **kwargs: Any) -> SupervisorCommand:
        logger.info("Supervisor Agent evaluating state for session %s (Current Status: %s)", state.session_id, state.status)
        
        # Base fallback logic implementing the required state machine
        if state.status in (InvestigationStatus.RECEIVED, InvestigationStatus.CREATED, InvestigationStatus.INITIALIZED):
            cmd = SupervisorCommand(
                action="NEXT_STAGE",
                next_stage=InvestigationStatus.INTAKE,
                rationale="New incident received. Commencing Intake phase.",
                confidence=1.0
            )
        elif state.status == InvestigationStatus.INTAKE:
            cmd = SupervisorCommand(
                action="NEXT_STAGE",
                next_stage=InvestigationStatus.PLANNING,
                rationale="Triage complete. Proceeding to diagnostic planning.",
                confidence=0.9
            )
        elif state.status == InvestigationStatus.PLANNING:
            cmd = SupervisorCommand(
                action="NEXT_STAGE",
                next_stage=InvestigationStatus.EVIDENCE,
                rationale="Diagnostic plan generated. Initiating parallel evidence collection.",
                confidence=0.9
            )
        elif state.status in (InvestigationStatus.COLLECTING_EVIDENCE, InvestigationStatus.EVIDENCE):
            cmd = SupervisorCommand(
                action="NEXT_STAGE",
                next_stage=InvestigationStatus.REASONING,
                rationale="Evidence collected. Initiating causal synthesis and adversarial review.",
                confidence=0.85
            )
        elif state.status in (InvestigationStatus.HYPOTHESIS_SYNTHESIS, InvestigationStatus.REASONING):
            # Check hypothesis confidence
            if state.hypotheses:
                top_hyp = state.hypotheses[0]
                if top_hyp.likelihood_score < 0.80:
                    cmd = SupervisorCommand(
                        action="LOOP_BACK",
                        next_stage=InvestigationStatus.EVIDENCE,
                        rationale=f"Highest hypothesis confidence is {top_hyp.likelihood_score}, which is below the 0.80 threshold. Re-initiating evidence collection.",
                        missing_information=["Additional log traces", "Code repository commit history"],
                        confidence=top_hyp.likelihood_score
                    )
                else:
                    cmd = SupervisorCommand(
                        action="NEXT_STAGE",
                        next_stage=InvestigationStatus.DECISION,
                        rationale="High confidence hypothesis verified. Moving to Remediation and Compliance Decision.",
                        confidence=top_hyp.likelihood_score
                    )
            else:
                cmd = SupervisorCommand(
                    action="LOOP_BACK",
                    next_stage=InvestigationStatus.EVIDENCE,
                    rationale="No hypotheses generated. Re-initiating evidence collection.",
                    confidence=0.0
                )
        elif state.status in (InvestigationStatus.REMEDIATION_READY, InvestigationStatus.DECISION):
            cmd = SupervisorCommand(
                action="NEXT_STAGE",
                next_stage=InvestigationStatus.REPORTING,
                rationale="Remediation architected and compliance verified. Generating final report.",
                confidence=0.95
            )
        elif state.status in (InvestigationStatus.PRODUCING_REPORT, InvestigationStatus.REPORTING):
            cmd = SupervisorCommand(
                action="TERMINATE",
                next_stage=InvestigationStatus.COMPLETED,
                rationale="Reporting complete. Investigation successfully archived.",
                terminate=True,
                confidence=1.0
            )
        else:
            cmd = SupervisorCommand(
                action="TERMINATE",
                next_stage=InvestigationStatus.COMPLETED,
                rationale="Unknown or terminal state reached.",
                terminate=True,
                confidence=1.0
            )

        # Allow LLM to override fallback if available
        if self.llm_provider and hasattr(self.llm_provider, "generate_step_structured"):
            context_data = {
                "current_status": state.status,
                "loop_count": state.loop_count,
                "evidence_count": len(state.universal_evidence),
                "hypotheses_count": len(state.hypotheses),
                "highest_hypothesis_score": state.hypotheses[0].likelihood_score if state.hypotheses else 0.0
            }
            try:
                llm_cmd = await self.llm_provider.generate_step_structured(
                    prompt_name="supervisor",
                    prompt_version="v1",
                    response_model=SupervisorCommand,
                    context={"state_summary": json.dumps(context_data, indent=2)},
                    temperature=0.1
                )
                logger.info("Supervisor Agent successfully made decision via LLM: %s -> %s", llm_cmd.action, llm_cmd.next_stage)
                return llm_cmd
            except Exception as e:
                logger.warning("LLM generation failed in SupervisorAgent, falling back to static rules: %s", e)

        logger.info("Supervisor Agent returning static decision: %s -> %s", cmd.action, cmd.next_stage)
        return cmd
