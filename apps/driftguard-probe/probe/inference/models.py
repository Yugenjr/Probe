from typing import Any, Dict, Optional, TypeVar, Generic
from pydantic import BaseModel

T = TypeVar("T")

class InferenceRequest(BaseModel):
    system_instructions: str
    user_payload: str
    target_schema_json: Dict[str, Any]
    model_identifier: str

class InferenceResult(BaseModel, Generic[T]):
    """
    Typed envelope returned by InferenceClient.
    Wraps the validated Pydantic domain artifact along with operational compute metadata.
    Reasoning modules consume exclusively the validated `.artifact`.
    """
    artifact: T
    model_identifier: str
    latency_ms: float
    retry_count: int
    token_usage_approx: int

    class Config:
        arbitrary_types_allowed = True
        frozen = True
