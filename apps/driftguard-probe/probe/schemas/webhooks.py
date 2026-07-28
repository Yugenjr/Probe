"""Webhook incident consumption schemas."""
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class WebhookPayload(BaseModel):
    """Payload incoming from MLOps monitoring platforms (DriftGuard, Arize, etc.)."""
    model_config = ConfigDict(populate_by_name=True, extra="ignore")
    source_platform: str = Field(default="driftguard", description="Originating monitoring solution")
    event_type: str = Field(default="drift_detected", description="Trigger event tag e.g. 'drift_detected'")
    model_id: str = Field(...)
    model_version: str = Field(default="latest", alias="version")
    drift_score: Optional[float] = Field(default=None)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: Dict[str, Any] = Field(default_factory=dict, description="Platform-specific anomaly metrics")
    webhook_secret: Optional[str] = Field(default=None, description="HMAC or token authorization verification stub")
    event_id: Optional[int] = Field(default=None, description="DriftGuard event ID")
    callback_url: Optional[str] = Field(default=None, description="Callback complete webhook URL")


class WebhookResponse(BaseModel):
    """Acknowledgement returned to originating platform."""
    investigation_id: str = Field(..., description="Unique ID assigned to tracking state")
    status: str = Field(default="ACCEPTED")
    message: str = Field(default="Investigation workflow dispatched asynchronously.")
