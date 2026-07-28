import json
import re
from typing import Any, Dict, Union
from .exceptions import MalformedResponseError

class ResponseParser:
    """
    Safely extracts and decodes structured JSON from backend response buffers.
    Rejects malformed text, empty strings, and partial syntax without mutating content.
    """
    @staticmethod
    def parse_to_dict(raw_content: Union[str, Dict[str, Any], None]) -> Dict[str, Any]:
        if raw_content is None:
            raise MalformedResponseError("[ResponseParser] Inference backend returned empty None payload.")

        if isinstance(raw_content, dict):
            if not raw_content:
                raise MalformedResponseError("[ResponseParser] Inference backend returned empty dictionary.")
            return raw_content

        if not isinstance(raw_content, str):
            raise MalformedResponseError(f"[ResponseParser] Unsupported response primitive: {type(raw_content)}")

        cleaned = raw_content.strip()
        if not cleaned:
            raise MalformedResponseError("[ResponseParser] Inference backend returned zero-length empty string.")

        # Safely decouple markdown code fences if present
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-z]*\n?", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\n?```$", "", cleaned).strip()

        try:
            parsed = json.loads(cleaned)
            if not isinstance(parsed, dict):
                raise MalformedResponseError(f"[ResponseParser] Expected JSON object root, got {type(parsed)}.")
            return parsed
        except json.JSONDecodeError as e:
            raise MalformedResponseError(
                f"[ResponseParser] JSON decoding failure: {str(e)} | Buffer prefix: {cleaned[:150]}"
            ) from e
