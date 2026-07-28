"""Evidence domain model with strongly typed discriminated union payloads."""
from enum import Enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .payloads import StructuredPayload, GenericDictPayload


class EvidenceType(str, Enum):
    """Classification of retrieved diagnostic evidence."""
    METRICS = "METRICS"
    DRIFT_STATS = "DRIFT_STATS"
    VALIDATION = "VALIDATION"
    AUDIT_LOG = "AUDIT_LOG"
    HISTORICAL_INCIDENT = "HISTORICAL_INCIDENT"
    DOCUMENTATION = "DOCUMENTATION"


class EvidenceItem(BaseModel):
    """Individual atomic piece of diagnostic evidence supported by strictly typed payload schemas."""
    evidence_id: str = Field(..., description="Unique evidence tracking ID")
    source_tool: str = Field(..., description="Tool name responsible for retrieving this item")
    evidence_type: EvidenceType = Field(...)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    summary: str = Field(..., description="Natural language digest of findings")
    data_payload: StructuredPayload = Field(
        default_factory=lambda: GenericDictPayload(payload_type="generic", data={}),
        description="Strongly typed telemetry or document retrieval payload",
    )
    relevance_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Estimated diagnostic significance")

    # TODO: Implementation pending for automated ranking and relevance weighting algorithms


class Evidence(BaseModel):
    """Collection of accrued evidence items for an investigation."""
    investigation_id: str
    items: List[EvidenceItem] = Field(default_factory=list)
