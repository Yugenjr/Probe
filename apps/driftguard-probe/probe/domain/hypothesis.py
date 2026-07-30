"""Hypothesis domain model representing causal root-cause diagnostic theories."""
from datetime import datetime, timezone
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class CausalHypothesis(BaseModel):
    """Causal root-cause theory synthesized by autonomous reasoning agents from accrued empirical evidence."""
    schema_version: str = Field(default="1.0.0", description="Semantic version of the CausalHypothesis contract")
    hypothesis_id: str = Field(..., description="Unique diagnostic hypothesis UUID")
    primary_root_cause: str = Field(..., description="The definitive root cause driving the anomaly")
    contributing_factors: List[str] = Field(default_factory=list, description="Additional factors that exacerbated the incident")
    causal_chain: List[str] = Field(default_factory=list, description="Chronological sequence of causal events")
    supporting_evidence: List[str] = Field(default_factory=list, description="Explicit IDs of accrued Evidence items validating this theory")
    contradicting_evidence: List[str] = Field(default_factory=list, description="Explicit IDs of accrued Evidence items contradicting this theory")
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Estimated confidence score in root cause accuracy",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CritiqueReport(BaseModel):
    """Structured red-team artifact challenging a proposed CausalHypothesis."""
    schema_version: str = Field(default="1.0.0", description="Semantic version of the CritiqueReport contract")
    overall_verdict: Literal["ACCEPT", "REJECT", "NEEDS_EVIDENCE"] = Field(..., description="Final judgement on the hypothesis")
    confidence_after_review: float = Field(..., ge=0.0, le=1.0, description="Revised confidence score after critical review")
    contradictions: List[str] = Field(default_factory=list, description="Identified logical contradictions within the hypothesis or evidence")
    unsupported_claims: List[str] = Field(default_factory=list, description="Claims made in the hypothesis without backing evidence")
    alternative_hypotheses: List[str] = Field(default_factory=list, description="Plausible alternative explanations for the symptoms")
    missing_evidence: List[str] = Field(default_factory=list, description="Types of evidence that should have been collected but were not")
    recommended_action: str = Field(..., description="Action recommended to the Supervisor (e.g. advance, gather more logs, escalate)")
    requires_more_evidence: bool = Field(default=False, description="Flag indicating if the Supervisor must loop back to gather evidence")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
