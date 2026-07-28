from abc import ABC, abstractmethod
from typing import List, Dict, Any

class RetrievalAdapter(ABC):
    @property
    @abstractmethod
    def source_type(self) -> str:
        pass

    @abstractmethod
    async def retrieve(self, query: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Retrieve context relevant to the query.
        Returns a list of structured documents or context blocks.
        """
        pass
