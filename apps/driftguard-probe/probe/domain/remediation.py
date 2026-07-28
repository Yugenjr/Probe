"""Remediation domain entity representing actionable engineering intervention proposals."""
from enum import Enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class InterventionType(str, Enum):
    """Categorization of proposed operational engineering remediations."""
    AUTOMATED_RETRAINING = "AUTOMATED_RETRAINING"
    CANARY_ROLLBACK = "CANARY_ROLLBACK"
    THRESHOLD_RELAXATION = "THRESHOLD_RELAXATION"
    TRAFFIC_THROTTLING = "TRAFFIC_THROTTLING"
    HUMAN_INTERVENTION_REQUIRED = "HUMAN_INTERVENTION_REQUIRED"


class RemediationPlan(BaseModel):
    """Actionable engineering intervention proposal formulated by remediation expert agents."""
    remediation_id: str = Field(..., description="Unique intervention proposal identifier")
    target_model_id: str = Field(..., description="Deployment target requiring remediation")
    intervention_type: InterventionType = Field(...)
    summary: str = Field(..., description="Executive briefing of required corrective action")
    execution_parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters required for CI/CD dispatch")
    supporting_hypothesis_id: Optional[str] = Field(default=None, description="ID of root cause hypothesis motivating this action")
    estimated_impact_percent: float = Field(default=0.0, description="Calculated simulated improvement to target metrics")
    requires_human_approval: bool = Field(default=True, description="Safety interlock preventing unassisted production overrides")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
