from typing import Optional
from pydantic import BaseModel, Field

class InferenceConfig(BaseModel):
    """
    Configuration for Probe Inference Engine.
    All endpoints and generation parameters are configurable; nothing is hardcoded.
    The deployed compute backend (vLLM, HuggingFace TGI, NVIDIA NIM) can be altered solely through this model.
    """
    endpoint: str = "http://localhost:8000/v1/chat/completions"
    authentication_token: str = "default-auth-token-do-not-log"
    model_identifier: str = "meta-llama/Llama-3.1-70B-Instruct"
    timeout_seconds: float = 15.0
    temperature: float = 0.1  # Low temperature for deterministic factual engineering inference
    top_p: float = 0.95
    max_tokens: int = 4096
    seed: int = 42
    reasoning_effort: Optional[str] = "high"  # Applicable for inference-heavy reasoning compute engines
    max_retries: int = 3
    retry_base_delay_seconds: float = 0.2

    class Config:
        frozen = True
