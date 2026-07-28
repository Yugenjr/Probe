"""Embedding vector transformer engines."""
import logging
from typing import List

logger = logging.getLogger(__name__)


class EmbeddingEngine:
    """Generates dense dense float embedding arrays from unstructured diagnostic text."""
    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.model_name = model_name

    async def embed_text(self, text: str) -> List[float]:
        """Convert a single text sequence into an embedding vector."""
        logger.debug("Generating embeddings using model %s", self.model_name)
        # TODO: Implementation pending for API calls to OpenAIExtension or SentenceTransformers
        return [0.0] * 384

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Convert an array of documents into parallel vector embeddings."""
        return [await self.embed_text(t) for t in texts]
