"""Hypothesis domain model representing causal root-cause diagnostic theories."""
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field


class Hypothesis(BaseModel):
    """Causal root-cause theory synthesized by autonomous reasoning agents from accrued empirical evidence."""
    hypothesis_id: str = Field(..., description="Unique diagnostic hypothesis UUID")
    title: str = Field(..., description="Concise statement of hypothesized causal failure pattern")
    detailed_reasoning: str = Field(..., description="Comprehensive empirical synthesis supporting this theory")
    supporting_evidence_ids: List[str] = Field(
        default_factory=list,
        description="Explicit IDs of accrued UniversalEvidence items mathematically validating this theory",
    )
    likelihood_score: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Estimated probability that this hypothesis represents the actual operational anomaly root cause",
    )
    verified_by_simulation: bool = Field(
        default=False,
        description="Status flag indicating whether automated replay testing validated this causal assumption",
    )
    explanation: str = Field(default="", description="Detailed explanation linking evidence to theoretical root cause")
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Estimated confidence score in root cause accuracy",
    )
    weaknesses: List[str] = Field(
        default_factory=list,
        description="Weaknesses of this hypothesis",
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def associate_evidence(self, evidence_id: str) -> None:
        """Attach supporting empirical evidence item reference to this hypothesis."""
        if evidence_id not in self.supporting_evidence_ids:
            self.supporting_evidence_ids.append(evidence_id)


class HypothesisCollection(BaseModel):
    """Collection of formulated hypotheses."""
    hypotheses: List[Hypothesis] = Field(default_factory=list)
