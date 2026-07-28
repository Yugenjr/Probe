"""Asynchronous worker consumer supporting distributed execution queues and local threading."""
import logging
import asyncio
from typing import Any, Dict
from ..domain.incident import Incident, IncidentSeverity
from .orchestrator import InvestigationOrchestrator
from .state import InvestigationSession

logger = logging.getLogger(__name__)


async def execute_background_investigation(incident_payload: Dict[str, Any]) -> InvestigationSession:
    """Consume async incident alert payload from message brokers and execute forensic investigation."""
    try:
        # Instantiate domain Incident entity from ingress transport payload
        incident = Incident(
            incident_id=str(incident_payload.get("incident_id", "inc-unknown")),
            model_id=str(incident_payload.get("model_id", "target-model")),
            source_platform=str(incident_payload.get("source_platform", "DriftGuard")),
            trigger_type=str(incident_payload.get("trigger_type", "anomaly_detected")),
            severity=IncidentSeverity(incident_payload.get("severity", "MEDIUM")),
        )
        orchestrator = InvestigationOrchestrator()
        session = await orchestrator.initiate_investigation(incident)
        completed_session = await orchestrator.execute_investigation_loop(session)
        
        logger.info("Successfully executed background forensic job for session %s", completed_session.session_id)
        return completed_session
    except Exception as exc:
        logger.error("Failed executing background investigation task: %s", str(exc), exc_info=True)
        raise


class WorkerService:
    """Worker service interface designed for seamless Celery or Temporal task integration."""
    @staticmethod
    def run_job_sync(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous invocation wrapper for standalone Celery worker daemons."""
        session = asyncio.run(execute_background_investigation(payload))
        return session.model_dump(mode="json")
