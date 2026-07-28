"""Tool input and output binding schemas for agent invocation."""
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ToolInputSchema(BaseModel):
    """Standardized invocation envelope passed from an agent to a tool."""
    tool_name: str = Field(...)
    investigation_id: str = Field(...)
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ToolOutputSchema(BaseModel):
    """Standardized response envelope returned by tool invocations."""
    tool_name: str = Field(...)
    investigation_id: str = Field(...)
    success: bool = Field(default=True)
    result_data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    execution_duration_ms: float = Field(default=0.0)

    # TODO: Implementation pending for detailed OpenTelemetry span metric serialization
