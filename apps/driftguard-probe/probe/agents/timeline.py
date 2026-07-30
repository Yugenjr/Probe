from .base import BaseAgent
import logging
from typing import List, Union
from ..engine.state import InvestigationSession
from ..domain.evidence import ChronologicalTimeline, EvidenceBundle, EvidenceSummary, UniversalEvidence
import uuid

logger = logging.getLogger(__name__)

class TimelineAnalystAgent(BaseAgent):

    @property
    def role_name(self) -> str:
        return "TimelineAnalyst"

    """Agent responsible for chronological sequencing, establishing causal chains, and detecting concurrent events."""
    
    async def execute(self, session: InvestigationSession, **kwargs) -> EvidenceBundle:
        logger.info("TimelineAnalystAgent synthesizing chronological timeline for session %s", session.session_id)
        evidence_list = session.universal_evidence
        
        # In a real scenario, the TimelineAnalystAgent would use the LLM to sort and synthesize the list of evidence
        # Here we mock the structural output
        timeline = ChronologicalTimeline(
            events=[{"timestamp": e.timestamp.isoformat(), "summary": e.summary} for e in evidence_list],
            probable_trigger="Feature flag 'enable_new_billing' deployment",
            causal_chain=[
                "Feature flag toggled",
                "NullPointerException in BillingService",
                "Metric drift in 'user_age' due to fallback routing"
            ],
            concurrent_events=["High CPU utilization on DB"],
            missing_time_ranges=[],
            confidence=0.88
        )
        
        # Compute summary
        metric_count = sum(1 for e in evidence_list if e.evidence_type in ("drift_stats", "performance_curve", "validation_run"))
        log_count = sum(1 for e in evidence_list if e.evidence_type == "log_trace")
        repo_count = sum(1 for e in evidence_list if e.evidence_type == "code_change")
        research_count = sum(1 for e in evidence_list if e.evidence_type in ("runbook_reference", "historical_incident", "known_failure_pattern"))
        
        summary = EvidenceSummary(
            metric_count=metric_count,
            log_count=log_count,
            repo_count=repo_count,
            runbook_matches=research_count,
            collection_duration=1.5,
            coverage_score=0.92
        )
        
        # Build the bundle
        bundle = EvidenceBundle(
            metrics=[e for e in evidence_list if e.evidence_type in ("drift_stats", "performance_curve", "validation_run")],
            logs=[e for e in evidence_list if e.evidence_type == "log_trace"],
            repo=[e for e in evidence_list if e.evidence_type == "code_change"],
            research=[e for e in evidence_list if e.evidence_type in ("runbook_reference", "historical_incident", "known_failure_pattern")],
            timeline=timeline,
            summary=summary
        )
        
        return bundle
