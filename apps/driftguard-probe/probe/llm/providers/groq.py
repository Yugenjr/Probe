"""Groq API provider adapter using OpenAI-compatible endpoints."""
import json
import logging
from typing import Any, Optional, Type, TypeVar
import httpx
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import BaseModel
from .base import BaseLLMProvider
from ..parser import parse_structured_output

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class GroqProvider(BaseLLMProvider):
    """Provider adapter communicating with Groq REST OpenAI-compatible inference endpoints."""

    def __init__(self, api_key: Optional[str] = None, model_name: str = "llama-3.1-8b-instant"):
        from ...core.config import get_settings
        settings = get_settings()
        self.api_key = api_key or settings.groq_api_key
        self.model_name = model_name
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10), retry=retry_if_exception_type(httpx.HTTPStatusError))
    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        logger.debug("Executing Groq generation on model %s", self.model_name)
        if not self.api_key:
            raise ValueError("Groq API key is not configured. Please set GROQ_API_KEY environment variable.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self.base_url, headers=headers, json=payload)
            if resp.status_code != 200:
                logger.error("Groq API error response status %s: %s", resp.status_code, resp.text)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=10), retry=retry_if_exception_type(httpx.HTTPStatusError))
    async def generate_structured(
        self,
        response_model: Type[T],
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> T:
        logger.debug("Executing Groq structured generation for schema %s", response_model.__name__)
        if not self.api_key:
            raise ValueError("Groq API key is not configured. Please set GROQ_API_KEY environment variable.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Inject instructions to ensure JSON output strictly complies with schema
        schema_json = json.dumps(response_model.model_json_schema(), indent=2)
        system_prompt += f"\n\nYou MUST return a JSON object that strictly adheres to this JSON Schema:\n{schema_json}"

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": 4096,
            "response_format": {"type": "json_object"}
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(self.base_url, headers=headers, json=payload)
            if resp.status_code != 200:
                logger.error("Groq API error response status %s: %s", resp.status_code, resp.text)
            resp.raise_for_status()
            data = resp.json()
            raw_content = data["choices"][0]["message"]["content"]
            return parse_structured_output(raw_content, response_model)
