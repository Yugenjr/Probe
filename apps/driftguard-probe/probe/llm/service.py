"""LLMService coordinating versioned prompts, rendering, provider selection, and latency/token metrics."""
import time
import json
import logging
from typing import Any, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel
from .providers import get_llm_provider, BaseLLMProvider
from .prompts import load_prompt_template
from ..interfaces.llm import LLMProvider

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class LLMService(LLMProvider):
    """Wrapper service implementing LLMProvider protocol, centralizing reasoning trace analytics."""

    def __init__(self, provider: Optional[BaseLLMProvider] = None):
        self.provider = provider or get_llm_provider()
        self.last_trace: Optional[Dict[str, Any]] = None

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        """Text generation delegation forwarding directly to backend provider."""
        return await self.provider.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )

    async def generate_structured(
        self,
        response_model: Type[T],
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> T:
        """Structured completion delegation forwarding directly to backend provider."""
        # Simple backward compatible pass-through
        return await self.provider.generate_structured(
            response_model=response_model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature
        )

    async def generate_step_structured(
        self,
        prompt_name: str,
        prompt_version: str,
        response_model: Type[T],
        context: Dict[str, Any],
        temperature: float = 0.1,
    ) -> T:
        """Load versioned prompt template, render context, evaluate structured output, and capture trace."""
        # 1. Load prompt template
        template = load_prompt_template(prompt_name, prompt_version)
        
        # 2. Render template variables dynamically
        rendered_prompt = template.template
        for k, v in context.items():
            val_str = json.dumps(v, indent=2) if isinstance(v, (dict, list)) else str(v)
            rendered_prompt = (
                rendered_prompt.replace("{{" + f" {k} " + "}}", val_str)
                .replace("{{" + k + "}}", val_str)
            )

        start_time = time.perf_counter()
        
        try:
            # 3. Call structured provider backend
            output = await self.provider.generate_structured(
                response_model=response_model,
                system_prompt=rendered_prompt,
                user_prompt="",
                temperature=temperature
            )
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            
            # 4. Generate ReasoningTrace metadata trace
            self.last_trace = {
                "agent": prompt_name,
                "model_name": getattr(self.provider, "model_name", "unknown"),
                "prompt_version": prompt_version,
                "latency_ms": duration_ms,
                "tokens_prompt": len(rendered_prompt) // 4,  # Rough token approximation fallback
                "tokens_completion": len(output.model_dump_json()) // 4,
                "total_tokens": (len(rendered_prompt) + len(output.model_dump_json())) // 4,
                "cost_estimate": 0.0,
                "success": True
            }
            logger.info("Structured step generation '%s' version '%s' completed in %.2fms", prompt_name, prompt_version, duration_ms)
            return output
            
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            self.last_trace = {
                "agent": prompt_name,
                "model_name": getattr(self.provider, "model_name", "unknown"),
                "prompt_version": prompt_version,
                "latency_ms": duration_ms,
                "tokens_prompt": len(rendered_prompt) // 4,
                "tokens_completion": 0,
                "total_tokens": len(rendered_prompt) // 4,
                "cost_estimate": 0.0,
                "success": False,
                "error_message": str(e)
            }
            logger.error("Structured step generation '%s' failed in %.2fms: %s", prompt_name, prompt_version, duration_ms, e)
            raise e


_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Acquire the global singleton instance of LLMService."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
