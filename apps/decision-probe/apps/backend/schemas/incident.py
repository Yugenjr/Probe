from pydantic import BaseModel
from typing import List, Literal

class IncidentResponse(BaseModel):
    incident_title: str
    summary: str
    affected_services: List[str]
    root_cause: str
    confidence: float
    current_status: Literal["investigating", "mitigated", "resolved"]
