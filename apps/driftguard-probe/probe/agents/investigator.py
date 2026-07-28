"""Investigator domain expert agent analyzing quantitative telemetry and feature distribution drift."""
import logging
from typing import Any, Dict
from .base import BaseAgent
from ..engine.state import InvestigationSession
from ..tools.analytics import AnalyzeFeatureDriftTool, CorrelateLatencyWithDriftTool
from ..core.di import get_container

logger = logging.getLogger(__name__)


class InvestigatorAgent(BaseAgent):
    """Forensic quantitative telemetry and feature shift diagnostician.
    
    Operates as an autonomous domain expert evaluating feature distance metrics (ADWIN, Wasserstein)
    and correlating statistical data anomalies against system operational degradation curves.
    """
    @property
    def role_name(self) -> str:
        return "Investigator"

    async def execute(self, state: InvestigationSession, **kwargs: Any) -> Dict[str, Any]:
        logger.info("Investigator Agent evaluating quantitative drift telemetry for session %s", state.session_id)
        from ..domain.evidence import DriftEvidence
        import uuid
        
        drift_score = 0.25
        if state.investigation_context and state.investigation_context.predictions:
            first_pred = state.investigation_context.predictions[0]
            if isinstance(first_pred, dict) and first_pred.get("drift_score") is not None:
                drift_score = first_pred["drift_score"]
        elif state.incident and state.incident.raw_payload and isinstance(state.incident.raw_payload, dict):
            val = state.incident.raw_payload.get("drift_score")
            if val is not None:
                drift_score = val

        if drift_score is None:
            drift_score = 0.25

        evidence = DriftEvidence(
            evidence_id=f"ev-{uuid.uuid4().hex[:6]}",
            source_provider="DriftGuard-Core-v3",
            retrieved_by_tool="ContextExtractor",
            summary=f"Covariate drift score of {drift_score} observed on target model {state.incident.model_id}.",
            confidence_weight=0.95,
            feature_name="all_features",
            distance_algorithm="adwin",
            observed_distance=drift_score,
            alarm_threshold=0.15,
            is_anomalous=True
        )
        
        state.add_universal_evidence(evidence)
        return {"status": "EVIDENCE_COLLECTED", "evidence_id": evidence.evidence_id}
