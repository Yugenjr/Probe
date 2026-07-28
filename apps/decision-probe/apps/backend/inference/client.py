import logging
import json
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ValidationError
from groq import AsyncGroq, AuthenticationError, PermissionDeniedError, RateLimitError, APIStatusError, APIConnectionError, APITimeoutError
from dotenv import load_dotenv

from services.models import ReasoningContext
from services.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)

load_dotenv()

class LLMPayload(BaseModel):
    id: Optional[str] = None
    type: str
    order: Optional[int] = None
    content: Dict[str, Any]

class LLMOperation(BaseModel):
    op: str
    target_id: Optional[str] = None
    payload: LLMPayload

class LLMResponse(BaseModel):
    operations: List[LLMOperation]

class InferenceClient:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        self.client = AsyncGroq(api_key=api_key)
        self.model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.prompt_builder = PromptBuilder()

    async def generate(self, context: ReasoningContext) -> LLMResponse:
        """
        Builds request, calls Groq, parses response, validates JSON,
        retries once if invalid JSON, and returns a structured response.
        """
        system_prompt = self.prompt_builder.build_system_prompt()
        user_prompt = self.prompt_builder.build_user_prompt(context)
        
        return await self._call_with_retries(user_prompt, system_prompt, retries=1)
        
    async def _call_with_retries(self, user_prompt: str, system_prompt: str, retries: int) -> LLMResponse:
        attempts = 0
        last_error = None
        
        while attempts <= retries:
            try:
                logger.info(f"Calling Groq model {self.model_name} (Attempt {attempts + 1})")
                
                response = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0
                )
                
                raw_text = response.choices[0].message.content
                if not raw_text:
                    raise ValueError("Empty response from LLM")
                    
                # Parse JSON
                data = json.loads(raw_text)
                
                # Sometimes LLM returns a single object instead of a list
                if isinstance(data, dict):
                    # If it looks like {"operations": [...]}, unwrap it
                    if "operations" in data and isinstance(data["operations"], list):
                        pass
                    # If it looks like {"op": "append_block", ...} or {"operation": ...}, wrap it
                    elif "op" in data or "operation" in data:
                        data = {"operations": [data]}
                    elif "operations" not in data:
                        # Sometimes it returns a top-level JSON that doesn't match the schema
                        # Wrap it in operations and assume it's a generic block payload if we can't do better
                        logger.warning(f"Unexpected JSON structure without operations key: {data}")
                        raise ValueError("Unexpected JSON structure without 'operations' key")
                elif isinstance(data, list):
                    data = {"operations": data}
                    
                # Fix common LLM mistake: 'operation' instead of 'op'
                for op_dict in data.get("operations", []):
                    if "operation" in op_dict and "op" not in op_dict:
                        op_dict["op"] = op_dict.pop("operation")
                    if "block" in op_dict and "payload" not in op_dict:
                        op_dict["payload"] = op_dict.pop("block")
                    if "payload" not in op_dict and "content" in op_dict:
                        # Sometimes they just put the block fields at the top level of payload
                        op_dict["payload"] = {
                            "type": op_dict.get("type", "unknown"),
                            "content": op_dict.pop("content")
                        }
                    
                # Validate against Pydantic models
                validated_response = LLMResponse(**data)
                
                logger.info("Successfully validated LLM response.")
                return validated_response
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to decode JSON: {e}")
                last_error = e
            except ValidationError as e:
                logger.warning(f"Validation error: {e}")
                last_error = e
            except AuthenticationError as e:
                logger.error(f"Authentication failed (401): {e}")
                last_error = e
                # Do not retry on auth error
                break
            except PermissionDeniedError as e:
                logger.error(f"Permission denied (403): {e}")
                last_error = e
                break
            except RateLimitError as e:
                logger.error(f"Rate limit exceeded (429): {e}")
                last_error = e
            except APIStatusError as e:
                logger.error(f"API returned status error ({e.status_code}): {e}")
                last_error = e
            except APITimeoutError as e:
                logger.error(f"API timeout: {e}")
                last_error = e
            except APIConnectionError as e:
                logger.error(f"API connection failure: {e}")
                last_error = e
            except Exception as e:
                logger.error(f"Inference error: {e}")
                last_error = e
                
            attempts += 1
            
        raise RuntimeError(f"Inference failed after {attempts} attempts. Last error: {last_error}")
