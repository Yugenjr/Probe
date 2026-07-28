"""Reporter Agent synthesizing comprehensive diagnostic documentation."""
import logging
import uuid
from typing import Any, Optional
from .base import BaseAgent
from ..core.state import InvestigationState
from ..models.report import InvestigationReport

logger = logging.getLogger(__name__)


class ReporterAgent(BaseAgent):
    """Specialized agent compiling verified evidence, hypotheses, and recommendations into markdown diagnostic reports."""
    @property
    def role_name(self) -> str:
        return "Reporter"

    async def execute(self, state: InvestigationState, **kwargs: Any) -> Optional[InvestigationReport]:
        logger.info("Reporter Agent generating executive report for session %s", state.investigation_id)
        primary_rc = state.hypotheses[0].title if state.hypotheses else "Unspecified anomaly cause."
        markdown = (
            f"# Incident Investigation Report: {state.investigation_id}\n\n"
            f"**Model ID:** {state.incident.model_id} ({state.incident.model_version})\n\n"
            f"## Primary Root Cause\n**{primary_rc}**\n\n"
            f"## Recommended Action\n"
            f"{state.recommendation.title if state.recommendation else 'None required.'}\n\n"
            f"*Report compiled autonomously via DriftGuard Probe platform-agnostic engine.*"
        )
        report = InvestigationReport(
            report_id=f"rep-{uuid.uuid4().hex[:6]}",
            investigation_id=state.investigation_id,
            incident_summary=state.incident,
            primary_root_cause=primary_rc,
            supporting_evidence=state.evidence_items,
            tested_hypotheses=state.hypotheses,
            experiments=state.experiments,
            recommended_action=state.recommendation,
            markdown_content=markdown,
        )
        state.report = report
        return report
