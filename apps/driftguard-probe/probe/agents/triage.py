"""Triage Agent assessing incident severity and investigation viability."""
import logging
import json
from typing import Any, Dict
from pydantic import BaseModel, Field
from .base import BaseAgent
from ..engine.state import InvestigationSession, InvestigationStatus

logger = logging.getLogger(__name__)

class TriageReport(BaseModel):
    """Schema representing the initial alert assessment."""
    severity: str = Field(..., description="Severity level: CRITICAL, HIGH, MEDIUM, LOW")
    priority: int = Field(..., description="Priority scale 1 (highest) to 5 (lowest)")
    confidence: float = Field(..., description="Confidence in the triage assessment (0.0 - 1.0)")
    recommended_strategy: str = Field(..., description="High-level strategy to investigate this alert")
    reason: str = Field(..., description="Rationale for the triage decision")
    proceed_with_investigation: bool = Field(..., description="Whether the incident warrants a full investigation")

class TriageAgent(BaseAgent):
    """First responder for incoming platform alerts to shed load and prioritize."""
    
    @property
    def role_name(self) -> str:
        return "Triage"

    async def execute(self, state: InvestigationSession, **kwargs: Any) -> Dict[str, Any]:
        logger.info("Triage Agent evaluating incident %s", state.incident.incident_id)
        
        fallback_report = TriageReport(
            severity="HIGH",
            priority=2,
            confidence=0.85,
            recommended_strategy="Prioritize investigating data distribution drift alongside inference latency.",
            reason="Anomaly trigger type matches high severity SLA degradation.",
            proceed_with_investigation=True
        )
        
        if self.llm_provider and hasattr(self.llm_provider, "generate_step_structured"):
            context_json = state.incident.model_dump_json(indent=2)
            try:
                report = await self.llm_provider.generate_step_structured(
                    prompt_name="triage",
                    prompt_version="v1",
                    response_model=TriageReport,
                    context={"incident_json": context_json},
                    temperature=0.1
                )
                logger.info("Triage Agent successfully assessed incident via LLM.")
                state.execution_history.append(f"[Triage] Assessed incident as {report.severity} severity (Proceed: {report.proceed_with_investigation}).")
                
                result = report.model_dump(mode="json")
                result["status"] = "TRIAGED"
                return result
            except Exception as e:
                logger.warning("LLM generation failed in TriageAgent, falling back to static report: %s", e)
        
        state.execution_history.append(f"[Triage] Assessed incident via Fallback as {fallback_report.severity} severity.")
        result = fallback_report.model_dump(mode="json")
        result["status"] = "TRIAGED"
        return result
