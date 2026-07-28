"""Recommendation domain model."""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


import uuid
from ..domain.hypothesis import Hypothesis

class RecommendationAction(str, Enum):
    """Actionable mitigation strategies for model remediation."""
    RETRAIN_MODEL = "RETRAIN_MODEL"
    ROLLBACK_MODEL = "ROLLBACK_MODEL"
    UPDATE_THRESHOLD = "UPDATE_THRESHOLD"
    RECALIBRATE = "RECALIBRATE"
    NO_ACTION_REQUIRED = "NO_ACTION_REQUIRED"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"


class Recommendation(BaseModel):
    """Actionable remediation guidance produced at completion of investigation."""
    # Legacy fields
    recommendation_id: str = Field(default_factory=lambda: f"rec-{uuid.uuid4().hex[:6]}")
    action_type: RecommendationAction = Field(default=RecommendationAction.ROLLBACK_MODEL)
    title: str = Field(default="", description="Executive summary of intervention step")
    justification: str = Field(default="", description="Root cause evidence justification")
    target_model_id: str = Field(default="")
    target_version: Optional[str] = Field(default=None, description="Recommended version target for rollback or retrain baseline")
    requires_human_approval: bool = Field(default=True, description="Safety latch requiring manual engineer consent before execution")

    # New fields
    action: str = Field(default="", description="Mitigation action e.g., 'Rollback'")
    reason: str = Field(default="", description="Justification for the action")
    priority: str = Field(default="P0", description="Priority level: P0, P1, P2")
    estimated_risk: str = Field(default="Low", description="Estimated risk: Low, Medium, High")
    estimated_time: str = Field(default="5 min", description="Estimated execution time")


class EvaluationResult(BaseModel):
    """Evaluation result assessing experimental evidence and recommending interventions."""
    best_hypothesis: Hypothesis
    alternatives: List[Hypothesis] = Field(default_factory=list)
    recommended_actions: List[Recommendation] = Field(default_factory=list)
    confidence: float = Field(default=0.5)

    # TODO: Implementation pending for automated automated webhook execution when approval granted
