"""Generic REST API requests and response schemas."""
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class APIRequest(BaseModel):
    """Base API request wrapping common audit attributes."""
    client_version: Optional[str] = Field(default="0.1.0")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class APIResponse(BaseModel):
    """Standard API envelope for successful responses."""
    status: str = Field(default="success")
    data: Dict[str, Any] = Field(default_factory=dict)
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response structure."""
    status: str = Field(default="error")
    error_code: str = Field(..., description="Machine-readable fault code")
    detail: str = Field(..., description="Human-readable diagnosis of error")
