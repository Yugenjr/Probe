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
    """Actionable mitigation strategies architected by the system to resolve the root cause."""
    schema_version: str = Field(default="1.0.0", description="Semantic version of the RemediationPlan contract")
    remediation_id: str = Field(..., description="Unique remediation UUID")
    immediate_actions: List[str] = Field(default_factory=list, description="Actions that must be taken immediately to mitigate impact")
    short_term_fix: str = Field(..., description="Proposed short-term resolution")
    long_term_fix: str = Field(..., description="Architectural or permanent resolution")
    rollback_plan: str = Field(..., description="Explicit commands or steps to rollback the system if the fix fails")
    risk_level: str = Field(..., description="Risk assessment of the proposed intervention (e.g. LOW, MEDIUM, HIGH)")
    estimated_impact: str = Field(..., description="Description of the expected outcome if the intervention succeeds")
    verification_steps: List[str] = Field(default_factory=list, description="Steps to manually or automatically verify the fix")
    requires_human_approval: bool = Field(default=True, description="Safety interlock preventing unassisted production overrides")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
