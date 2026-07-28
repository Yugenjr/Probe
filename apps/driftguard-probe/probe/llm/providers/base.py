"""Abstract base implementation for generative LLM providers."""
from abc import ABC, abstractmethod
from typing import Type, TypeVar
from pydantic import BaseModel
from ...interfaces.llm import LLMProvider

T = TypeVar("T", bound=BaseModel)


class BaseLLMProvider(ABC, LLMProvider):
    """Base class enforcing uniform asynchronous inference signatures across different vendors."""

    @abstractmethod
    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        """Generate unstructured textual completion."""
        pass

    @abstractmethod
    async def generate_structured(
        self,
        response_model: Type[T],
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> T:
        """Generate structured Pydantic domain response."""
        pass
