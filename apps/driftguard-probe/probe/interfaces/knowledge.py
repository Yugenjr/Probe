"""Knowledge and organizational memory retrieval interface protocol definition."""
from typing import Any, Dict, List, Protocol, runtime_checkable


@runtime_checkable
class KnowledgeProvider(Protocol):
    """Protocol defining organizational runbook extraction and semantic historical incident queries.
    
    Enables qualitative reasoning agents to correlate live anomalies against documented resolutions.
    """
    async def search_runbooks(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve historical operational runbook documentation and step-by-step resolution guides."""
        ...

    async def fetch_historical_incidents(self, anomaly_signature: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """Query vector stores for historical validated root causes matching active anomaly signatures."""
        ...
