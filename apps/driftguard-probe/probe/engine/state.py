"""Immutable versioned investigation session state schemas for distributed execution."""
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from ..domain.incident import Incident
from ..domain.hypothesis import CausalHypothesis, CritiqueReport
from ..domain.remediation import RemediationPlan
from ..domain.evidence import (
    DriftEvidence,
    PerformanceCurveEvidence,
    ValidationRunEvidence,
    RunbookReferenceEvidence,
    UniversalEvidence,
    EvidenceBundle,
)
from ..context.models import InvestigationContext
# Backward-compatibility alias for legacy tests and workflows
from ..models.evidence import EvidenceItem
from ..models.recommendation import EvaluationResult
from ..mcp.capability import EvidencePlan
from ..domain.graph import EvidenceGraph


class InvestigationResult(BaseModel):
    """Immutable final outcome of the reasoning and decision pipeline."""
    schema_version: str = Field(default="1.0.0", description="Semantic version of the InvestigationResult contract")
    investigation_id: str = Field(..., description="Unique runtime investigation UUID")
    evidence_bundle: EvidenceBundle
    evidence_graph: EvidenceGraph
    causal_hypothesis: CausalHypothesis
    critique_report: CritiqueReport
    remediation_plan: RemediationPlan
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InvestigationStatus(str, Enum):
    """Exhaustive lifecycle execution phases governing automated forensic investigations."""
    RECEIVED = "RECEIVED"
    CREATED = "CREATED"
    INITIALIZED = "INITIALIZED"
    INTAKE = "INTAKE"
    PLANNING = "PLANNING"
    EVIDENCE = "EVIDENCE"
    REASONING = "REASONING"
    DECISION = "DECISION"
    REPORTING = "REPORTING"
    COLLECTING_EVIDENCE = "COLLECTING_EVIDENCE"
    RESEARCHING = "RESEARCHING" # Legacy workflow compatibility
    ANALYZING = "ANALYZING" # Legacy workflow compatibility
    HYPOTHESIS_SYNTHESIS = "HYPOTHESIS_SYNTHESIS"
    GENERATING_HYPOTHESIS = "GENERATING_HYPOTHESIS" # Legacy workflow compatibility
    SYNTHESIZING_HYPOTHESIS = "SYNTHESIZING_HYPOTHESIS" # Legacy workflow compatibility
    EXPERIMENTAL_VALIDATION = "EXPERIMENTAL_VALIDATION"
    TESTING_HYPOTHESIS = "TESTING_HYPOTHESIS" # Legacy workflow compatibility
    REMEDIATION_READY = "REMEDIATION_READY"
    PRODUCING_REPORT = "PRODUCING_REPORT" # Legacy workflow compatibility
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AgentResult(BaseModel):
    """Execution audit snapshot returned by a completed agent invocation."""
    agent_name: str
    started_at: datetime
    finished_at: datetime
    success: bool
    output: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)
    cost: float = 0.0
    tokens: int = 0
    latency: float
    retries: int = 0

class SupervisorDecision(BaseModel):
    """Immutable audit record of orchestration decisions."""
    id: str = Field(..., description="Unique decision ID")
    investigation_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    action: str
    stage: str
    confidence: float
    required_agents: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    rationale: str
    request_reason: Optional[str] = None


class InvestigationSession(BaseModel):
    """Runtime execution state representing the active investigation session.
    
    Provides structured mutation helpers and immutable snapshot generation to guarantee
    data race safety across distributed parallel asynchronous worker threads.
    """
    session_id: str = Field(..., description="Unique runtime investigation UUID")
    investigation_id: str = Field(..., description="Backwards-compatible investigation identifier alias")
    status: InvestigationStatus = Field(default=InvestigationStatus.RECEIVED)
    investigation_goal: Optional[str] = Field(default=None, description="The primary objective of the investigation")
    incident: Incident
    investigation_context: Optional[InvestigationContext] = None
    active_workflow_name: Optional[str] = Field(default=None, description="Active deterministic workflow loop name")
    universal_evidence: List[UniversalEvidence] = Field(default_factory=list, description="Strictly typed domain evidence items")
    evidence_items: List[EvidenceItem] = Field(default_factory=list, description="Legacy general evidence list for compatibility")
    hypotheses: List[Any] = Field(default_factory=list) # Legacy backward compatibility
    evaluation_result: Optional[EvaluationResult] = None
    remediation_plan: Optional[RemediationPlan] = None
    evidence_plan: Optional[EvidencePlan] = None
    evidence_bundle: Optional[EvidenceBundle] = None
    evidence_graph: Optional[EvidenceGraph] = None
    causal_hypothesis: Optional[CausalHypothesis] = None
    critique_report: Optional[CritiqueReport] = None
    investigation_result: Optional[InvestigationResult] = None
    report: Optional[Any] = None
    historical_pattern_analysis: Optional[Any] = None

    supervisor_decisions: List[SupervisorDecision] = Field(default_factory=list, description="Audit log of Supervisor commands")
    agent_results: List[AgentResult] = Field(default_factory=list, description="Completed agent execution trace results")
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    execution_history: List[str] = Field(default_factory=list, description="Chronological audit trace of state transitions")
    loop_count: int = Field(default=0, description="Number of backward stage loops taken")
    max_loops: int = Field(default=3, description="Configurable maximum threshold for backward stage loops before escalation")

    def transition_to(self, new_status: InvestigationStatus, log_entry: Optional[str] = None) -> None:
        """Advance the investigation lifecycle state machine and record atomic transition logs."""
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)
        if log_entry:
            self.execution_history.append(f"[{self.updated_at.isoformat()}] [{new_status.value}] {log_entry}")
        if new_status in (InvestigationStatus.COMPLETED, InvestigationStatus.FAILED):
            self.completed_at = self.updated_at

    def add_universal_evidence(self, item: UniversalEvidence) -> None:
        """Safely attach strictly typed UniversalEvidence item with audit trace logging."""
        self.universal_evidence.append(item)
        self.updated_at = datetime.now(timezone.utc)
        self.execution_history.append(
            f"[{self.updated_at.isoformat()}] [Evidence] Accrued {item.evidence_type} evidence from {item.source_provider}."
        )

    def add_evidence(self, item: EvidenceItem) -> None:
        """Backwards-compatible legacy evidence insertion method."""
        self.evidence_items.append(item)
        self.updated_at = datetime.now(timezone.utc)
        self.execution_history.append(
            f"[{self.updated_at.isoformat()}] [Evidence] Accrued item {item.evidence_id} from {item.source_tool}."
        )

    def add_hypothesis(self, hypothesis: Any) -> None:
        """Safely attach synthesized causal root-cause hypothesis to active state."""
        self.hypotheses.append(hypothesis)
        self.updated_at = datetime.now(timezone.utc)
        self.execution_history.append(
            f"[{self.updated_at.isoformat()}] [Hypothesis] Synthesized legacy hypothesis."
        )

    def attach_remediation(self, plan: RemediationPlan) -> None:
        """Attach verified actionable engineering intervention proposal."""
        self.remediation_plan = plan
        self.updated_at = datetime.now(timezone.utc)
        self.execution_history.append(
            f"[{self.updated_at.isoformat()}] [Remediation] Formulated intervention {plan.remediation_id} ({plan.intervention_type.value})."
        )

    def create_immutable_snapshot(self) -> "InvestigationSession":
        """Generate a deep copy snapshot of the runtime session.
        
        Essential for safe async transmission across EventBus broadcast topics and database serializers
        without risking concurrent mutation race conditions.
        """
        return self.model_copy(deep=True)


# Backwards compatible alias for legacy test fixtures and CoreSupervisor
InvestigationState = InvestigationSession
