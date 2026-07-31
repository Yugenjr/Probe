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
        self._api_keys = ["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"]
        self.model_name = model_name
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

    _key_index = 0

    @property
    def api_key(self) -> Optional[str]:
        if not self._api_keys:
            return None
        key = self._api_keys[self.__class__._key_index % len(self._api_keys)]
        self.__class__._key_index += 1
        return key

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        logger.debug("Executing Groq generation on model %s", self.model_name)
        while True:
            current_key = self.api_key
            if not current_key:
                raise ValueError("Groq API key is not configured.")

            headers = {
                "Authorization": f"Bearer {current_key}",
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
                if resp.status_code == 429:
                    logger.warning("Groq API rate limit hit. Sleeping 20s before retrying...")
                    await asyncio.sleep(20)
                    continue
                elif resp.status_code == 413:
                    logger.error("Groq API 413: Payload too large. Raising without retry.")
                    resp.raise_for_status()
                elif resp.status_code != 200:
                    logger.error("Groq API error response status %s: %s", resp.status_code, resp.text)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]

    async def generate_structured(
        self,
        response_model: Type[T],
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> T:
        logger.debug("Executing Groq structured generation for schema %s", response_model.__name__)
        
        schema_json = json.dumps(response_model.model_json_schema(), indent=2)
        system_prompt += (
            f"\n\nYou MUST return a valid JSON object containing the actual data. "
            f"Do NOT return the schema definition itself. "
            f"Your response must be an instance that strictly adheres to this JSON Schema:\n{schema_json}"
        )

        while True:
            current_key = self.api_key
            if not current_key:
                raise ValueError("Groq API key is not configured.")

            headers = {
                "Authorization": f"Bearer {current_key}",
                "Content-Type": "application/json"
            }
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
                if resp.status_code == 429:
                    logger.warning("Groq API rate limit hit in structured. Sleeping 20s...")
                    await asyncio.sleep(20)
                    continue
                elif resp.status_code == 413:
                    logger.error("Groq API 413: Payload too large. Raising without retry.")
                    resp.raise_for_status()
                elif resp.status_code != 200:
                    logger.error("Groq API error response status %s: %s", resp.status_code, resp.text)
                resp.raise_for_status()
                
                data = resp.json()
                raw_content = data["choices"][0]["message"]["content"]
                return parse_structured_output(raw_content, response_model)
