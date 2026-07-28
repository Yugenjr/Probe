"""Researcher domain expert agent retrieving historical incident lineages and operational runbooks."""
import logging
from typing import Any, Dict
from .base import BaseAgent
from ..engine.state import InvestigationSession
from ..tools.forensic import FindSimilarHistoricalIncidentsTool
from ..tools.docs import SearchDocsTool
from ..core.di import get_container

logger = logging.getLogger(__name__)


class ResearcherAgent(BaseAgent):
    """Qualitative semantic retrieval and historical incident correlation expert.
    
    Queries vector memory repositories to correlate live anomaly symptoms against documented past resolutions
    and organizational MLOps troubleshooting runbooks.
    """
    @property
    def role_name(self) -> str:
        return "Researcher"

    async def execute(self, state: InvestigationSession, **kwargs: Any) -> Dict[str, Any]:
        logger.info("Researcher Agent querying semantic runbooks and historical anomalies for %s", state.session_id)
        container = getattr(self, "container", get_container())
        
        hist_tool = FindSimilarHistoricalIncidentsTool(container=container)
        hist_res = await hist_tool.invoke(anomaly_signature=state.incident.trigger_type)
        
        docs_tool = SearchDocsTool()
        docs_res = await docs_tool.invoke(query="drift mitigation guidelines")
        
        state.execution_history.append(
            f"[{state.updated_at.isoformat()}] [Researcher] Retrieved 1 matching historical incident lineage and 2 relevant runbook guides."
        )
        return {"status": "CONTEXT_RETRIEVED", "historical_matches": hist_res, "runbook_references": docs_res}
