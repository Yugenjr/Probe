import json
from typing import Dict, List, Any
from pydantic import BaseModel, Field
from probe.shared.hashing import compute_canonical_sha256

class Evidence(BaseModel):
    """
    Base Evidence immutable model.
    IDs are deterministically generated via SHA-256 canonical hashing over payload attributes.
    Running extraction twice produces identical IDs.
    """
    id: str
    type: str
    provider: str
    timestamp: str
    source: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    confidence: float
    relationships: List[str] = Field(default_factory=list)
    hash: str
    origin: str

    class Config:
        frozen = True
        arbitrary_types_allowed = True

    @classmethod
    def generate_deterministic(
        cls,
        type: str,
        provider: str,
        timestamp: str,
        source: str,
        payload: Dict[str, Any],
        confidence: float,
        relationships: List[str],
        origin: str
    ) -> "Evidence":
        canonical_target = {
            "type": type,
            "provider": provider,
            "timestamp": timestamp,
            "source": source,
            "payload": payload
        }
        sha_hash = compute_canonical_sha256(canonical_target)
        deterministic_id = f"ev-{sha_hash[:16]}"
        
        return cls(
            id=deterministic_id,
            type=type,
            provider=provider,
            timestamp=timestamp,
            source=source,
            payload=payload,
            confidence=float(confidence),
            relationships=sorted(list(set(relationships))),
            hash=sha_hash,
            origin=origin
        )

# Specialized domain evidence subclasses inheriting from common base
class DriftEvidence(Evidence):
    pass

class ValidationEvidence(Evidence):
    pass

class AuditEvidence(Evidence):
    pass

class TelemetryEvidence(Evidence):
    pass

class MetricEvidence(Evidence):
    pass

class ModelEvidence(Evidence):
    pass

class RetrainingEvidence(Evidence):
    pass

class PredictionEvidence(Evidence):
    pass

class ReportEvidence(Evidence):
    pass
