"""Universal domain evidence model hierarchy utilizing Pydantic v2 discriminated unions."""
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class BaseEvidence(BaseModel):
    """Abstract foundational evidence class guaranteeing universal origin tracking and immutable audit history."""
    evidence_id: str = Field(..., description="Globally unique cryptographic identifier for evidence item")
    source_provider: str = Field(..., description="Origin provider adapter name e.g. 'DriftGuardAdapter' or 'WhyLabsAdapter'")
    retrieved_by_tool: str = Field(..., description="Analytical diagnostic tool responsible for generating this evidence")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    summary: str = Field(..., description="Natural language digest structured for agent semantic comprehension")
    confidence_weight: float = Field(default=1.0, ge=0.0, le=1.0, description="Estimated empirical reliability weight")
    relevance_score: float = Field(default=0.0, description="Score indicating relevance to the current investigation")
    evidence_type: str


class DriftEvidence(BaseEvidence):
    """Strongly typed evidence representing statistical feature distribution drift and anomalies."""
    evidence_type: Literal["drift_stats"] = "drift_stats"
    feature_name: str
    distance_algorithm: Literal["adwin", "ks_test", "wasserstein", "psi", "kl_divergence", "custom"] = "adwin"
    observed_distance: float
    alarm_threshold: float = 0.05
    is_anomalous: bool = True


class PerformanceCurveEvidence(BaseEvidence):
    """Strongly typed operational time-series performance degradation evidence."""
    evidence_type: Literal["performance_curve"] = "performance_curve"
    metric_name: str
    timestamps: List[str] = Field(default_factory=list)
    values: List[float] = Field(default_factory=list)
    baseline_average: float = 0.0
    current_deviation_percent: float = 0.0


class ValidationRunEvidence(BaseEvidence):
    """Strongly typed verification outcome record from automated upstream dataset test suites."""
    evidence_type: Literal["validation_run"] = "validation_run"
    check_id: str
    passed: bool
    failed_record_count: int = 0
    rule_description: str = ""


class RunbookReferenceEvidence(BaseEvidence):
    """Strongly typed qualitative runbook retrieval and documentation evidence."""
    evidence_type: Literal["runbook_reference"] = "runbook_reference"
    runbook_id: str
    section_title: str
    recommended_actions: List[str] = Field(default_factory=list)


class LogTraceEvidence(BaseEvidence):
    evidence_type: Literal["log_trace"] = "log_trace"
    log_level: str
    message: str
    stack_trace: Optional[str] = None
    correlation_id: Optional[str] = None

class CodeChangeEvidence(BaseEvidence):
    evidence_type: Literal["code_change"] = "code_change"
    change_type: Literal["commit", "pr", "release", "config", "feature_flag", "deployment"]
    author: str
    description: str
    diff_summary: str

class HistoricalIncidentEvidence(BaseEvidence):
    evidence_type: Literal["historical_incident"] = "historical_incident"
    past_incident_id: str
    similarity_score: float
    resolution_status: str
    root_cause: str

class KnownFailurePattern(BaseEvidence):
    evidence_type: Literal["known_failure_pattern"] = "known_failure_pattern"
    pattern_name: str
    description: str
    symptoms: List[str] = Field(default_factory=list)

class ChronologicalTimeline(BaseModel):
    events: List[Dict[str, Any]] = Field(default_factory=list)
    probable_trigger: Optional[str] = None
    causal_chain: List[str] = Field(default_factory=list)
    concurrent_events: List[str] = Field(default_factory=list)
    missing_time_ranges: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0)

class EvidenceSummary(BaseModel):
    metric_count: int = 0
    log_count: int = 0
    repo_count: int = 0
    runbook_matches: int = 0
    collection_duration: float = 0.0
    coverage_score: float = 0.0

# Discriminated Union type for compile-time structural guarantees and automatic JSON schema verification
UniversalEvidence = Union[
    DriftEvidence,
    PerformanceCurveEvidence,
    ValidationRunEvidence,
    RunbookReferenceEvidence,
    LogTraceEvidence,
    CodeChangeEvidence,
    HistoricalIncidentEvidence,
    KnownFailurePattern,
]

class EvidenceBundle(BaseModel):
    status: Literal["COMPLETE", "PARTIAL", "FAILED"] = "COMPLETE"
    metrics: List[Union[DriftEvidence, PerformanceCurveEvidence, ValidationRunEvidence]] = Field(default_factory=list)
    logs: List[LogTraceEvidence] = Field(default_factory=list)
    repo: List[CodeChangeEvidence] = Field(default_factory=list)
    research: List[Union[RunbookReferenceEvidence, HistoricalIncidentEvidence, KnownFailurePattern]] = Field(default_factory=list)
    timeline: Optional[ChronologicalTimeline] = None
    summary: Optional[EvidenceSummary] = None
    collection_started_at: Optional[datetime] = None
    collection_finished_at: Optional[datetime] = None
    total_duration: float = 0.0
    failed_agents: List[str] = Field(default_factory=list)
    successful_agents: List[str] = Field(default_factory=list)
