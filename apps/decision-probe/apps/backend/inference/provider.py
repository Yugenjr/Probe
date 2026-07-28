from abc import ABC, abstractmethod
from typing import List, Dict, Any

class InferenceProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def generate_patches(self, context: str, user_prompt: str) -> List[Dict[str, Any]]:
        """
        Generate a list of patch operations based on the workspace context and user prompt.
        Must return structured JSON array matching the PatchOperation schema.
        """
        pass
