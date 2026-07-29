from pydantic import BaseModel
from typing import List

class FailurePrediction(BaseModel):
    service: str
    predicted_issue: str
    confidence: float
    estimated_time_window: str
    reasoning: List[str]

class PredictionResponse(BaseModel):
    predictions: List[FailurePrediction]
    generated_at: str = ""
