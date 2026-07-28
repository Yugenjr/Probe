"""Internal REST transfer structures for DriftGuard responses."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DriftGuardModelDTO(BaseModel):
    """Data Transfer Object representing model metadata retrieved via REST."""
    model_id: str
    version: str
    framework: Optional[str] = None
    status: str = "active"
    metrics: Dict[str, Any] = Field(default_factory=dict)


class DriftGuardMetricDTO(BaseModel):
    """Data Transfer Object for time series telemetry datapoints."""
    metric_name: str
    timestamp: str
    value: float


class DriftGuardAuditDTO(BaseModel):
    """Data Transfer Object for governance log entries."""
    log_id: int
    event_type: str
    timestamp: str
    details: str
