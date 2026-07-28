from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class InvestigationStatus(str, Enum):
    DETECTED = "DETECTED"
    CREATED = "CREATED"
    CONTEXT_GATHERED = "CONTEXT_GATHERED"
    EVIDENCE_READY = "EVIDENCE_READY"
    REPORT_GENERATED = "REPORT_GENERATED"
    RECOMMENDATION_PENDING = "RECOMMENDATION_PENDING"
    CLOSED_RESOLVED = "CLOSED_RESOLVED"
    FAILED_ABANDONED = "FAILED_ABANDONED"
    PARTIAL_DATA_DEGRADED = "PARTIAL_DATA_DEGRADED"

class InvestigationRecord(BaseModel):
    investigation_id: str
    tenant_id: str
    trigger_source: str
    target_resource_id: str  # e.g. "fraud-v2" or "inc-001"
    status: InvestigationStatus = InvestigationStatus.CREATED
    created_at_utc: str
    updated_at_utc: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
