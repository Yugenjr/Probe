"""Ollama local LLM provider adapter."""
import logging
from typing import Type, TypeVar
from pydantic import BaseModel
from .base import BaseLLMProvider
from ..parser import parse_structured_output

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class OllamaProvider(BaseLLMProvider):
    """Provider adapter communicating with local Ollama deployment instances."""
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "llama3"):
        self.base_url = base_url
        self.model_name = model_name

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        logger.debug("Executing local Ollama generation on model %s at %s", self.model_name, self.base_url)
        # TODO: Implementation pending for async local HTTP interactions with Ollama /api/generate
        return "Simulated local Ollama analysis."

    async def generate_structured(
        self,
        response_model: Type[T],
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> T:
        logger.debug("Executing local Ollama JSON extraction for schema %s", response_model.__name__)
        # TODO: Implementation pending for Ollama schema grammar enforcement
        dummy_json = "{}"
        return parse_structured_output(dummy_json, response_model)
