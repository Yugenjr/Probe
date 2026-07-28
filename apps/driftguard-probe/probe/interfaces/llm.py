"""LLM Provider protocol abstractions."""
from typing import Any, Dict, Optional, Protocol, Type, TypeVar, runtime_checkable
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


@runtime_checkable
class LLMProvider(Protocol):
    """Abstract interface for generative LLM providers (OpenAI, Anthropic, Ollama, etc.)."""

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        """Generate unstructured conversational or descriptive textual reasoning."""
        ...

    async def generate_structured(
        self,
        response_model: Type[T],
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> T:
        """Generate validated Pydantic v2 structured domain model output."""
        ...
