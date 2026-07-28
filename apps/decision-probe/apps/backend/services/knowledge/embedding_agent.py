import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

# Try importing google-genai
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

class EmbeddingAgent:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.use_real_client = GENAI_AVAILABLE and bool(self.api_key) and self.api_key != "dummy"
        
        # In-memory storage mock abstraction layer
        self.mock_store = {}

        if self.use_real_client:
            logger.info("Knowledge Embedding Agent initializing real GenAI Client.")
            self.client = genai.Client(api_key=self.api_key)
        else:
            logger.warning("Knowledge Embedding Agent running in OFFLINE/MOCK mode.")
            self.client = None

    async def embed_incident(
        self,
        incident_id: str,
        title: str,
        root_cause: str,
        services: List[str]
    ) -> Dict[str, Any]:
        """
        Embeds the incident details and caches it in the modular mock storage provider.
        """
        logger.info(f"Generating searchable vectors for incident: {incident_id}")
        
        # Abstraction layer cache store
        self.mock_store[incident_id] = {
            "title": title,
            "root_cause": root_cause,
            "services": services
        }

        return {
            "incident_id": incident_id,
            "embedding_metadata": {
                "title": title,
                "root_cause": root_cause,
                "services": services
            }
        }
