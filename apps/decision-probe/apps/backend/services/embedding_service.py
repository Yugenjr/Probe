import os
import json
import hashlib
import logging
from typing import List
import numpy as np

logger = logging.getLogger(__name__)

# Try importing the official google-genai package
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-genai package is not available. Embedding service will run in offline mock mode.")

class EmbeddingService:
    def __init__(self):
        # We check both GEMINI_API_KEY and general configuration
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.use_real_client = GENAI_AVAILABLE and bool(self.api_key) and self.api_key != "dummy"
        
        if self.use_real_client:
            logger.info("Initializing real GenAI Client for embeddings.")
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("Running EmbeddingService in OFFLINE/MOCK mode.")
            self.client = None

    async def get_embedding(self, text: str) -> List[float]:
        """
        Generates a 768-dimensional embedding vector for the given text.
        Uses Gemini text-embedding-004 model if API key is present.
        Otherwise, falls back to a deterministic normalized mock vector.
        """
        if not text:
            return [0.0] * 768

        if self.use_real_client:
            try:
                # Call Gemini API
                response = self.client.models.embed_content(
                    model="text-embedding-004",
                    contents=text
                )
                if response.embeddings and len(response.embeddings) > 0:
                    return response.embeddings[0].values
            except Exception as e:
                logger.error(f"Error calling Gemini embedding API: {e}. Falling back to mock.")
        
        # Fallback / Offline / Mock Mode
        return self._generate_deterministic_mock_vector(text)

    def _generate_deterministic_mock_vector(self, text: str, dimension: int = 768) -> List[float]:
        """
        Generates a deterministic 768-dimensional vector based on the content of the text.
        This allows testing and offline usage to perform realistic cosine similarity checks.
        """
        # Hash the text to generate a seed
        hash_bytes = hashlib.sha256(text.encode('utf-8')).digest()
        seed = int.from_bytes(hash_bytes[:4], byteorder='big')
        
        # Use numpy with the seed to generate a vector
        rng = np.random.default_rng(seed)
        vector = rng.standard_normal(dimension)
        
        # Normalize the vector to unit length
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector.tolist()

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        """
        Calculates cosine similarity between two vectors.
        """
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        
        arr1 = np.array(v1)
        arr2 = np.array(v2)
        
        dot_product = np.dot(arr1, arr2)
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)
        
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0
            
        return float(dot_product / (norm1 * norm2))
