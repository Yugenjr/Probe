"""Memory Agents orchestrating bidirectional learning (Recall and Learn)."""
import logging
from typing import Any, Dict, Optional
from .base import BaseAgent
from ..engine.state import InvestigationSession, InvestigationStatus
from ..domain.memory import HistoricalPatternAnalysis, InvestigationRecord, OutcomeFeedback
from ..services.memory import MemoryRetrievalService, MemoryStorageService

logger = logging.getLogger(__name__)


class MemoryRecallAgent(BaseAgent):
    """Proactively retrieves historical context before evidence gathering."""
    def __init__(self, retrieval_service: Optional[MemoryRetrievalService] = None, **kwargs: Any):
        super().__init__(**kwargs)
        self.retrieval_service = retrieval_service or MemoryRetrievalService()

    @property
    def role_name(self) -> str:
        return "MemoryRecall"

    async def execute(self, session: InvestigationSession, **kwargs: Any) -> HistoricalPatternAnalysis:
        """Fetch historical patterns for the incident."""
        logger.info("Memory Recall Agent fetching context for incident %s", session.incident.incident_id)
        
        goal = session.investigation_goal or ""
        analysis = await self.retrieval_service.recall(session.incident, goal)
        return analysis


class MemoryLearnAgent(BaseAgent):
    """Archives the completed investigation into the knowledge base."""
    def __init__(self, storage_service: Optional[MemoryStorageService] = None, **kwargs: Any):
        super().__init__(**kwargs)
        self.storage_service = storage_service or MemoryStorageService()

    @property
    def role_name(self) -> str:
        return "MemoryLearn"

    async def execute(
        self, 
        session: InvestigationSession, 
        actual_outcome: Optional[OutcomeFeedback] = None,
        **kwargs: Any
    ) -> None:
        """Package and store the InvestigationRecord."""
        logger.info("Memory Learn Agent archiving investigation %s", session.session_id)
        
        if not session.investigation_result:
            logger.warning("No InvestigationResult found to archive.")
            return

        # Ensure all evidence properties are retrieved from session safely
        # Note: Depending on orchestrator logic, some objects might be directly inside investigation_result.
        record = InvestigationRecord(
            investigation_id=session.session_id,
            investigation_result=session.investigation_result,
            evidence_bundle=session.investigation_result.evidence_bundle,
            evidence_graph=session.investigation_result.evidence_graph,
            supervisor_decisions=session.supervisor_decisions,
            memory_analysis=session.historical_pattern_analysis,
            actual_outcome=actual_outcome
        )
        
        await self.storage_service.store(record)
