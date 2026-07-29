from pydantic import BaseModel
from typing import List

class ServiceRisk(BaseModel):
    service: str
    risk_score: int
    risk_level: str  # Low | Moderate | High | Critical
    contributors: List[str]

class RiskScoreResponse(BaseModel):
    services: List[ServiceRisk]
    generated_at: str = ""
