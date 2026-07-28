from typing import List, Dict, Any
from .provider import InferenceProvider

class MockProvider(InferenceProvider):
    @property
    def name(self) -> str:
        return "MockProvider"

    async def generate_patches(self, context: str, user_prompt: str) -> List[Dict[str, Any]]:
        # Mocking an LLM response that returns a structured patch operation
        return [
            {
                "op": "append_block",
                "target_id": "workspace_id_mock",
                "payload": {
                    "type": "reasoning",
                    "content": {
                        "text": f"Mock reasoning for: {user_prompt}"
                    }
                }
            }
        ]
