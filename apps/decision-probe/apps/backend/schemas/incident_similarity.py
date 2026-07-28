from pydantic import BaseModel
from typing import List

class SimilarIncidentItem(BaseModel):
    incident_id: str
    similarity_score: float
    root_cause: str
    solution: str

class IncidentSimilarityResponse(BaseModel):
    similar_incidents: List[SimilarIncidentItem]
