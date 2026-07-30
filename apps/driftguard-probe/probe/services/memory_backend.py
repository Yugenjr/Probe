"""Abstract interface for the Memory Backend."""
import abc
from typing import Dict, Any, List

class MemoryBackend(abc.ABC):
    """Abstract interface defining required storage capabilities.
    
    This abstracts away concrete infrastructure (Neo4j, Qdrant, Postgres) from the reasoning logic.
    """
    
    @abc.abstractmethod
    async def retrieve(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Retrieve historical context matching the given parameters."""
        pass

    @abc.abstractmethod
    async def store(self, record_id: str, payload: Dict[str, Any]) -> None:
        """Store an InvestigationRecord persistently."""
        pass
