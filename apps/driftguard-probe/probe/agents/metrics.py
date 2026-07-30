from .base import BaseAgent
import logging
from typing import Optional, List, Union
from ..engine.state import InvestigationSession
from ..domain.evidence import DriftEvidence, PerformanceCurveEvidence
import uuid

logger = logging.getLogger(__name__)

class MetricAnalystAgent(BaseAgent):

    @property
    def role_name(self) -> str:
        return "MetricAnalyst"

    """Agent responsible for analyzing telemetry, drift metrics, and statistical performance curves."""
    
    async def execute(self, session: InvestigationSession) -> List[Union[DriftEvidence, PerformanceCurveEvidence]]:
        logger.info("MetricAnalystAgent analyzing telemetry for session %s", session.session_id)
        # Mock logic representing fallback static evidence generation
        # In a real scenario, this would query a metrics backend via MCP
        
        # Example drift evidence
        evidence_drift = DriftEvidence(
            evidence_id=str(uuid.uuid4()),
            source_provider="DriftGuardAdapter",
            retrieved_by_tool="MetricAnalystAgent",
            summary="Significant statistical drift detected in feature 'user_age'.",
            confidence_weight=0.85,
            relevance_score=0.9,
            feature_name="user_age",
            distance_algorithm="wasserstein",
            observed_distance=0.12,
            alarm_threshold=0.05,
            is_anomalous=True
        )
        
        return [evidence_drift]
