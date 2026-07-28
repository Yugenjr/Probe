"""Hypothesis domain model."""
from enum import Enum
from typing import List
from pydantic import BaseModel, Field


class HypothesisLikelihood(str, Enum):
    """Estimated confidence score in root cause accuracy."""
    UNLIKELY = "UNLIKELY"
    POSSIBLE = "POSSIBLE"
    PROBABLE = "PROBABLE"
    HIGHLY_PROBABLE = "HIGHLY_PROBABLE"


class Hypothesis(BaseModel):
    """Testable theory explaining observed anomaly metrics."""
    hypothesis_id: str = Field(..., description="Unique hypothesis tag e.g., 'HYP-001'")
    title: str = Field(..., description="Concise statement of assumed failure mechanism")
    description: str = Field(..., description="Detailed explanation linking evidence to theoretical root cause")
    likelihood: HypothesisLikelihood = Field(default=HypothesisLikelihood.POSSIBLE)
    supporting_evidence_ids: List[str] = Field(default_factory=list, description="List of evidence IDs justifying this hypothesis")
    tested: bool = Field(default=False, description="Whether an experiment has evaluated this hypothesis")
    refuted: bool = Field(default=False, description="Whether experimental testing proved hypothesis incorrect")

    # TODO: Implementation pending for confidence updates based on Bayesian evaluation results
