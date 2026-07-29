from pydantic import BaseModel
from typing import List

class Anomaly(BaseModel):
    metric: str
    expected: float
    actual: float
    severity: str  # Low | Medium | High | Critical
    description: str

class AnomalyResponse(BaseModel):
    anomalies: List[Anomaly]
    generated_at: str = ""
