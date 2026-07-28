"""Experiment domain model."""
from enum import Enum
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ExperimentStatus(str, Enum):
    """Execution lifecycle status of validation experiment."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class ExperimentResult(BaseModel):
    """Quantitative measurement outcome of validation test."""
    metric_name: str
    observed_value: float
    threshold_value: Optional[float] = None
    passed_validation: bool = False


class Experiment(BaseModel):
    """Analytical replay or simulation designed to validate or refute an active hypothesis."""
    experiment_id: str = Field(..., description="Unique experiment run ID")
    hypothesis_id: str = Field(..., description="Target hypothesis under evaluation")
    tool_name: str = Field(..., description="Tool or runner tasked with execution")
    input_params: Dict[str, Any] = Field(default_factory=dict, description="Configuration parameters passed to evaluator")
    status: ExperimentStatus = Field(default=ExperimentStatus.PENDING)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    result: Optional[ExperimentResult] = None
    error_message: Optional[str] = None

    # TODO: Implementation pending for distributed background execution tracking
