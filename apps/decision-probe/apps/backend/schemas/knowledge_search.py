from pydantic import BaseModel
from typing import Dict, Any, List

class EmbeddingMetadata(BaseModel):
    title: str
    root_cause: str
    services: List[str]

class KnowledgeSearchResponse(BaseModel):
    incident_id: str
    embedding_metadata: EmbeddingMetadata
