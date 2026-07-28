"""Strongly typed discriminated payload models for evidence items and tool outputs."""
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class BasePayload(BaseModel):
    """Base model for all typed investigation payloads."""
    payload_type: str


class DriftStatsPayload(BasePayload):
    """Structured telemetry metrics representing calculated statistical distribution drift."""
    payload_type: Literal["drift_stats"] = "drift_stats"
    observed_drift_score: float = Field(..., description="Calculated statistical distance e.g. ADWIN or KS value")
    feature_name: str = Field(..., description="Input feature or embedding dimension experiencing anomaly")
    threshold_value: Optional[float] = Field(default=0.05, description="Triggering alarm threshold")
    algorithm: str = Field(default="adwin", description="Statistical hypothesis testing algorithm")


class MetricCurvePayload(BasePayload):
    """Structured operational time-series telemetry curve data."""
    payload_type: Literal["metric_curve"] = "metric_curve"
    metric_name: str
    values: List[float] = Field(default_factory=list)
    timestamps: List[str] = Field(default_factory=list)


class ValidationRunPayload(BasePayload):
    """Structured outcome record from automated data and schema validation test suites."""
    payload_type: Literal["validation_run"] = "validation_run"
    check_id: str
    passed: bool
    details: str
    failed_record_count: int = 0


class AuditTrailPayload(BasePayload):
    """Structured historical operational log record."""
    payload_type: Literal["audit_trail"] = "audit_trail"
    log_id: int
    event_type: str
    timestamp: str
    details: str
    operator: str = "system"


class RunbookMatchPayload(BasePayload):
    """Structured semantic documentation and runbook retrieval result."""
    payload_type: Literal["runbook_match"] = "runbook_match"
    runbook_id: str
    title: str
    section_uri: Optional[str] = None
    recommended_mitigation_steps: List[str] = Field(default_factory=list)


class GenericDictPayload(BasePayload):
    """Safe fallback structured wrapper for legacy unstructured external platform events."""
    payload_type: Literal["generic"] = "generic"
    data: Dict[str, Any] = Field(default_factory=dict)


# Discriminated Union type for compile-time safety and automatic JSON parsing validation
StructuredPayload = Union[
    DriftStatsPayload,
    MetricCurvePayload,
    ValidationRunPayload,
    AuditTrailPayload,
    RunbookMatchPayload,
    GenericDictPayload,
]
