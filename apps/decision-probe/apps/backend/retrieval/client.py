from typing import List, Dict, Any
from .adapter import RetrievalAdapter

class RetrievalClient:
    def __init__(self, adapters: List[RetrievalAdapter]):
        self.adapters = adapters
        
    async def retrieve_all(self, query: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        results = []
        for adapter in self.adapters:
            adapter_results = await adapter.retrieve(query, context)
            results.extend(adapter_results)
        return results
