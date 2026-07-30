"""Memory domain models for bidirectional learning capabilities."""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid

from .evidence import EvidenceBundle
from .graph import EvidenceGraph
from .hypothesis import CausalHypothesis, CritiqueReport
from .remediation import RemediationPlan


class HistoricalPatternAnalysis(BaseModel):
    """Proactive historical context retrieved prior to evidence collection."""
    schema_version: str = Field(default="1.0.0", frozen=True)
    analysis_id: str = Field(default_factory=lambda: f"mem-{uuid.uuid4().hex[:8]}")
    similar_incidents: List[str] = Field(default_factory=list, description="IDs of past similar incidents")
    successful_remediations: List[str] = Field(default_factory=list, description="Remediation steps that previously worked")
    failed_remediations: List[str] = Field(default_factory=list, description="Remediation steps that failed")
    match_explanations: List[str] = Field(default_factory=list, description="Why these past incidents were deemed similar")
    retrieval_sources: List[str] = Field(default_factory=list, description="Which stores provided the context (e.g. Vector, Graph)")
    retrieval_confidence: float = Field(default=0.0, description="Confidence in the relevance of historical context")
    common_root_causes: List[str] = Field(default_factory=list, description="Most frequent root causes for these symptoms")
    recurring_false_positives: List[str] = Field(default_factory=list, description="Hypotheses commonly mistaken for root causes here")
    recommended_evidence: List[str] = Field(default_factory=list, description="Specific evidence types recommended to gather")
    recommended_checks: List[str] = Field(default_factory=list, description="Specific deterministic checks to run")


class OutcomeFeedback(BaseModel):
    """Structured Experience Feedback detailing the real-world success of an investigation's remediation."""
    resolved: bool = Field(..., description="Did the remediation solve the incident?")
    resolution_time: str = Field(..., description="Time taken to resolve")
    post_remediation_metrics: Dict[str, Any] = Field(default_factory=dict, description="Metrics observed after remediation")
    manual_override: bool = Field(default=False, description="Whether a human had to intervene or modify the fix")
    operator_notes: Optional[str] = Field(default=None, description="Free-form text from the operator")


class InvestigationRecord(BaseModel):
    """Immutable archive of an entire investigation lifecycle, used for Memory Learn."""
    record_version: str = Field(default="1.0.0", frozen=True)
    investigation_id: str = Field(...)
    archived_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Core artifacts
    investigation_result: Any
    evidence_bundle: EvidenceBundle
    evidence_graph: EvidenceGraph
    
    # Orchestration history
    supervisor_decisions: List[Any] = Field(default_factory=list)
    
    # Memory Context
    memory_analysis: Optional[HistoricalPatternAnalysis] = None
    
    # Post-Investigation Metrics & Feedback
    quality_metrics: Dict[str, Any] = Field(
        default_factory=lambda: {
            "investigation_duration": "0s",
            "evidence_coverage": 0.0,
            "reasoning_confidence": 0.0,
            "false_positive_probability": 0.0,
            "remediation_success_probability": 0.0
        }
    )
    actual_outcome: Optional[OutcomeFeedback] = None
