"""LLM provider concrete integrations."""
from typing import Optional
from .base import BaseLLMProvider
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .ollama import OllamaProvider
from .groq import GroqProvider

__all__ = [
    "BaseLLMProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "OllamaProvider",
    "GroqProvider",
    "get_llm_provider",
]


def get_llm_provider(provider_name: Optional[str] = None) -> BaseLLMProvider:
    """Resolve and instantiate the target LLM provider based on settings or name."""
    from ...core.config import get_settings
    settings = get_settings()
    name = (provider_name or settings.llm_provider).lower()
    
    if name == "groq":
        return GroqProvider()
    elif name == "anthropic":
        return AnthropicProvider(api_key=settings.anthropic_api_key)
    elif name == "ollama":
        return OllamaProvider(base_url=settings.ollama_base_url)
    else:
        return OpenAIProvider(api_key=settings.openai_api_key)
