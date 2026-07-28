import datetime
import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ImmutableArtifact(BaseModel):
    """
    Base immutable schema for inter-agent communication in Probe.
    Reasoning agents MUST NOT exchange natural language strings; they exchange these schemas.
    """
    artifact_id: str
    investigation_id: str
    timestamp_utc: str
    producer_agent: str
    sha256_parent_evidence_ids: List[str] = Field(default_factory=list)

    class Config:
        frozen = True
        arbitrary_types_allowed = True

class HypothesisArtifact(ImmutableArtifact):
    hypothesis_id: str
    root_cause_title: str
    causal_chain_description: str
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    initial_confidence: float = 0.0
    required_verification_queries: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    confidence_inputs: Dict[str, Any] = Field(default_factory=dict)
    reasoning_trace: List[str] = Field(default_factory=list)
    uncertainty: str = "LOW"  # e.g., "LOW", "MEDIUM", "HIGH", "INSUFFICIENT_EVIDENCE"


class CounterEvidenceArtifact(ImmutableArtifact):
    target_hypothesis_id: str
    contradicting_evidence_ids: List[str]
    falsification_reasoning: str
    confidence_penalty: float

class ValidationArtifact(ImmutableArtifact):
    hypothesis_id: str
    is_verified: bool
    final_bayesian_confidence: float
    corroberated_evidence_count: int
    contradiction_count: int
    critic_notes: str

class RemediationArtifact(ImmutableArtifact):
    remediation_id: str
    target_hypothesis_id: str
    action_type: str  # e.g., "ROLLBACK_AND_RETRAIN", "UPDATE_PROMPT_GUARD"
    execution_parameters: Dict[str, Any] = Field(default_factory=dict)
    estimated_impact_recovery: float
    risk_assessment: str  # "LOW", "MEDIUM", "HIGH"
    required_approval_tier: str  # "AUTOMATED", "SRE_LEAD", "EXECUTIVE"

class InvestigationReport(ImmutableArtifact):
    report_id: str
    dominant_hypothesis: HypothesisArtifact
    critic_validation: ValidationArtifact
    proposed_remediation: RemediationArtifact
    complete_lineage_hash: str
