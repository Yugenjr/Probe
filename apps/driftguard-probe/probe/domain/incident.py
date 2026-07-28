"""Incident domain entity representing anomaly detections from external monitoring platforms."""
from enum import Enum
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class IncidentSeverity(str, Enum):
    """Operational urgency classification of detected ML incidents."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentStatus(str, Enum):
    """Lifecycle progress status of detected ML operational anomalies."""
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class Incident(BaseModel):
    """Immutable domain entity representing an incident received from a connected monitoring platform."""
    incident_id: str = Field(..., description="Globally unique anomaly incident identifier")
    model_id: str = Field(..., description="Target model deployment identifier")
    model_version: Optional[str] = Field(default=None, description="Architecture or checkpoint version")
    source_platform: str = Field(default="DriftGuard", description="Name of external monitoring provider")
    trigger_type: str = Field(default="drift_detected", description="Originating anomaly category e.g. 'drift_detected' or 'latency_spike'")
    severity: IncidentSeverity = Field(default=IncidentSeverity.MEDIUM)
    status: IncidentStatus = Field(default=IncidentStatus.OPEN)
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_payload: Dict[str, Any] = Field(default_factory=dict, description="Raw ingestion webhook data for backward compatibility")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional contextual routing parameters")
