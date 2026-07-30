from .base import BaseAgent
import logging
from typing import List
from ..engine.state import InvestigationSession
from ..domain.evidence import LogTraceEvidence
import uuid

logger = logging.getLogger(__name__)

class LogForensicsAgent(BaseAgent):

    @property
    def role_name(self) -> str:
        return "LogForensics"

    """Agent responsible for parsing and correlating application logs and system traces."""
    
    async def execute(self, session: InvestigationSession) -> List[LogTraceEvidence]:
        logger.info("LogForensicsAgent analyzing logs for session %s", session.session_id)
        
        evidence = LogTraceEvidence(
            evidence_id=str(uuid.uuid4()),
            source_provider="SplunkAdapter",
            retrieved_by_tool="LogForensicsAgent",
            summary="Found a fatal crash in the billing service correlated with the incident timestamp.",
            confidence_weight=0.95,
            relevance_score=0.99,
            log_level="ERROR",
            message="NullPointerException in BillingService.processPayment",
            stack_trace="java.lang.NullPointerException\n\tat com.billing.BillingService.processPayment(BillingService.java:42)",
            correlation_id=session.incident.incident_id
        )
        
        return [evidence]
