"""Memory Agent orchestrating immutable snapshot archiving and vector index compaction."""
import logging
from typing import Any, Dict, Optional
from .base import BaseAgent
from ..core.state import InvestigationState
from ..memory.retriever import KnowledgeRetriever
from ..memory.store import VectorStore

logger = logging.getLogger(__name__)


class MemoryAgent(BaseAgent):
    """Vector Store & Semantic Indexing Orchestrator Agent.
    
    Adhering to strict system architecture: Memory infrastructure resides in `probe/memory/`.
    The MemoryAgent acts as an authoritative orchestrator that takes immutable snapshots
    of completed investigations and indexes them into vector embedding collections for long-term lineage tracking.
    """
    def __init__(self, retriever: Optional[KnowledgeRetriever] = None, store: Optional[VectorStore] = None, **kwargs: Any):
        super().__init__(**kwargs)
        self.retriever = retriever or KnowledgeRetriever()
        self.store = store or VectorStore()

    @property
    def role_name(self) -> str:
        return "Memory"

    async def execute(self, state: InvestigationState, **kwargs: Any) -> Dict[str, Any]:
        """Index an immutable snapshot of a completed investigation into vector repositories."""
        logger.info("Memory Agent creating immutable archive snapshot for %s", state.investigation_id)
        snapshot = state.create_snapshot()
        content = snapshot.report.markdown_content if snapshot.report else f"Incident on {snapshot.incident.model_id}: {snapshot.status.value}"
        
        await self.store.store_document(
            collection="incidents",
            doc_id=snapshot.investigation_id,
            content=content,
            metadata={"model_id": snapshot.incident.model_id, "status": snapshot.status.value},
        )
        state.execution_history.append(
            f"[{state.updated_at.isoformat()}] [Memory] Immutable snapshot archived into vector store under 'incidents' collection."
        )
        return {"archived_id": snapshot.investigation_id, "collection": "incidents", "snapshot_immutable": True}
