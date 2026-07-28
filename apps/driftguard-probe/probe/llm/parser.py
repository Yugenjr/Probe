"""Structured JSON output schema parsing and validation utilities."""
import json
import logging
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


def parse_structured_output(raw_text: str, schema_class: Type[T]) -> T:
    """Safely extract and parse JSON markdown code blocks into target Pydantic schema."""
    cleaned_text = raw_text.strip()
    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text.lstrip("```json").rstrip("```").strip()
    elif cleaned_text.startswith("```"):
        cleaned_text = cleaned_text.lstrip("```").rstrip("```").strip()

    try:
        data = json.loads(cleaned_text)
        return schema_class.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as exc:
        logger.error("Failed to validate structured output for schema %s: %s", schema_class.__name__, str(exc))
        # TODO: Implementation pending for auto-healing prompt formatting retry triggers
        raise
