"""Memory infrastructure protocol abstractions."""
from typing import Any, Dict, List, Protocol, runtime_checkable


@runtime_checkable
class MemoryProvider(Protocol):
    """Abstract interface for embedding store and vector knowledge retrieval."""

    async def store_document(
        self,
        collection: str,
        doc_id: str,
        content: str,
        metadata: Dict[str, Any],
    ) -> None:
        """Embed and persist textual artifacts or incident traces."""
        ...

    async def retrieve_similar(
        self,
        collection: str,
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Retrieve top-K semantically analogous historical records or docs."""
        ...

    async def summarize_context(self, text_chunks: List[str], max_length: int = 500) -> str:
        """Compress lengthy historical traces into dense summary snapshots."""
        ...
