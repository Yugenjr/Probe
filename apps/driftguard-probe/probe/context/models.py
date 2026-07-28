from typing import Dict, List, Any
from pydantic import BaseModel, Field

class InvestigationContext(BaseModel):
    """
    Production-ready immutable schema representing consolidated diagnostic artifacts.
    Serves as the unalterable input to Evidence Extractor.
    """
    investigation_id: str
    tenant_id: str = "default"
    timestamp_utc: str
    provider_name: str
    incident: Dict[str, Any] = Field(default_factory=dict)
    model: Dict[str, Any] = Field(default_factory=dict)
    model_version: str = ""
    monitor: Dict[str, Any] = Field(default_factory=dict)
    drift: Dict[str, Any] = Field(default_factory=dict)
    validation: Dict[str, Any] = Field(default_factory=dict)
    audit: List[Dict[str, Any]] = Field(default_factory=list)
    retraining: List[Dict[str, Any]] = Field(default_factory=list)
    telemetry: List[Dict[str, Any]] = Field(default_factory=list)
    predictions: List[Dict[str, Any]] = Field(default_factory=list)
    reports: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    relationships: Dict[str, List[str]] = Field(default_factory=dict)

    class Config:
        frozen = True
        arbitrary_types_allowed = True
