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
        container = getattr(self, "container", get_container())
        
        drift_tool = AnalyzeFeatureDriftTool(container=container)
        drift_res = await drift_tool.invoke(model_id=state.incident.model_id)
        
        corr_tool = CorrelateLatencyWithDriftTool(container=container)
        corr_res = await corr_tool.invoke(model_id=state.incident.model_id)
        
        state.execution_history.append(
            f"[{state.updated_at.isoformat()}] [Investigator] Evaluated drift score ({drift_res.get('observed_distance')}) with p99 latency correlation ({corr_res.get('correlation_coefficient')})."
        )
        return {"status": "EVIDENCE_COLLECTED", "drift_metrics": drift_res, "latency_correlation": corr_res}
