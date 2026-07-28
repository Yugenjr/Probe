import json
import logging
from typing import List, Dict, Any
from sqlmodel import Session, select
import storage.database
from storage.models import DocumentChunk, Document
from services.embedding_service import EmbeddingService
from .adapter import RetrievalAdapter

logger = logging.getLogger(__name__)

class DocumentRetrievalAdapter(RetrievalAdapter):
    @property
    def source_type(self) -> str:
        return "document"

    def __init__(self, session: Session = None):
        self.session = session
        self.embedding_service = EmbeddingService()

    async def retrieve(self, query: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Retrieves the top-k most relevant chunks for a query in a workspace.
        Context dictionary must contain: {'workspace_id': str}
        Optional context: {'limit': int}
        """
        if not context or "workspace_id" not in context:
            logger.warning("Retrieval requested without workspace_id context. Returning empty.")
            return []

        workspace_id = context["workspace_id"]
        limit = context.get("limit", 5)

        logger.info(f"Retrieving chunks for query: '{query}' in workspace {workspace_id}")

        # Compute query embedding vector
        query_vector = await self.embedding_service.get_embedding(query)

        # Retrieve chunks matching workspace_id
        active_session = self.session if self.session else Session(storage.database.engine)
        try:
            statement = select(DocumentChunk).where(DocumentChunk.workspace_id == workspace_id)
            chunks = active_session.exec(statement).all()

            scored_chunks = []
            for chunk in chunks:
                try:
                    chunk_vector = json.loads(chunk.embedding_json)
                    sim = self.embedding_service.cosine_similarity(query_vector, chunk_vector)
                    scored_chunks.append((chunk, sim))
                except Exception as e:
                    logger.error(f"Error parsing embedding for chunk {chunk.id}: {e}")
                    continue

            # Sort by similarity score descending
            scored_chunks.sort(key=lambda x: x[1], reverse=True)

            results = []
            for chunk, score in scored_chunks[:limit]:
                # Fetch corresponding document title
                doc_title = "Unknown File"
                doc = active_session.get(Document, chunk.document_id)
                if doc:
                    doc_title = doc.filename
                
                results.append({
                    "id": chunk.id,
                    "document_id": chunk.document_id,
                    "title": doc_title,
                    "snippet": chunk.content,
                    "chunk_index": chunk.chunk_index,
                    "score": score,
                    "source": "document"
                })

            logger.info(f"Retrieved {len(results)} relevant chunks.")
            return results
        finally:
            if not self.session:
                active_session.close()
