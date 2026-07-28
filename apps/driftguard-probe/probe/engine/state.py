"""Immutable versioned investigation session state schemas for distributed execution."""
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from ..domain.incident import Incident
from ..domain.hypothesis import Hypothesis
from ..domain.remediation import RemediationPlan
from ..domain.evidence import (
    DriftEvidence,
    PerformanceCurveEvidence,
    ValidationRunEvidence,
    RunbookReferenceEvidence,
    UniversalEvidence,
)
from ..context.models import InvestigationContext
# Backward-compatibility alias for legacy tests and workflows
from ..models.evidence import EvidenceItem


class InvestigationStatus(str, Enum):
    """Exhaustive lifecycle execution phases governing automated forensic investigations."""
    RECEIVED = "RECEIVED"
    CREATED = "CREATED"
    PLANNING = "PLANNING"
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


class InvestigationSession(BaseModel):
    """Runtime execution state representing the active investigation session.
    
    Provides structured mutation helpers and immutable snapshot generation to guarantee
    data race safety across distributed parallel asynchronous worker threads.
    """
    session_id: str = Field(..., description="Unique runtime investigation UUID")
    investigation_id: str = Field(..., description="Backwards-compatible investigation identifier alias")
    status: InvestigationStatus = Field(default=InvestigationStatus.RECEIVED)
    incident: Incident
    investigation_context: Optional[InvestigationContext] = None
    active_workflow_name: Optional[str] = Field(default=None, description="Active deterministic workflow loop name")
    universal_evidence: List[UniversalEvidence] = Field(default_factory=list, description="Strictly typed domain evidence items")
    evidence_items: List[EvidenceItem] = Field(default_factory=list, description="Legacy general evidence list for compatibility")
    hypotheses: List[Hypothesis] = Field(default_factory=list)
    remediation_plan: Optional[RemediationPlan] = None
    report: Optional[Any] = None
    agent_results: List[AgentResult] = Field(default_factory=list, description="Completed agent execution trace results")
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    execution_history: List[str] = Field(default_factory=list, description="Chronological audit trace of state transitions")

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

    def add_hypothesis(self, hypothesis: Hypothesis) -> None:
        """Safely attach synthesized causal root-cause hypothesis to active state."""
        self.hypotheses.append(hypothesis)
        self.updated_at = datetime.now(timezone.utc)
        self.execution_history.append(
            f"[{self.updated_at.isoformat()}] [Hypothesis] Synthesized {hypothesis.hypothesis_id}: {hypothesis.title} (Likelihood: {hypothesis.likelihood_score})."
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
