"""Recommendation domain model."""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


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
    recommendation_id: str = Field(..., description="Unique remediation guidance ID")
    action_type: RecommendationAction = Field(...)
    title: str = Field(..., description="Executive summary of intervention step")
    justification: str = Field(..., description="Root cause evidence justification")
    target_model_id: str = Field(...)
    target_version: Optional[str] = Field(default=None, description="Recommended version target for rollback or retrain baseline")
    requires_human_approval: bool = Field(default=True, description="Safety latch requiring manual engineer consent before execution")

    # TODO: Implementation pending for automated automated webhook execution when approval granted
