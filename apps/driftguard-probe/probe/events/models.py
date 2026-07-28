"""Structured event models and domain classifications."""
from enum import Enum
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Domain telemetry events generated during investigations."""
    INCIDENT_RECEIVED = "INCIDENT_RECEIVED"
    WORKFLOW_STARTED = "WORKFLOW_STARTED"
    AGENT_ACTIVATED = "AGENT_ACTIVATED"
    TOOL_INVOKED = "TOOL_INVOKED"
    EVIDENCE_ACQUIRED = "EVIDENCE_ACQUIRED"
    HYPOTHESIS_PROCESSED = "HYPOTHESIS_PROCESSED"
    INVESTIGATION_FINALIZED = "INVESTIGATOR_FINALIZED"
    SYSTEM_ERROR = "SYSTEM_ERROR"


class DomainEvent(BaseModel):
    """Immutable message payload passed over the event bus."""
    event_id: str = Field(...)
    event_type: EventType = Field(...)
    investigation_id: Optional[str] = Field(default=None)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_module: str = Field(...)
    attributes: Dict[str, Any] = Field(default_factory=dict)

    # TODO: Implementation pending for automated serialization to OTLP trace attributes
