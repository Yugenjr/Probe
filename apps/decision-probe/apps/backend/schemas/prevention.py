from pydantic import BaseModel
from typing import List

class PreventiveRecommendation(BaseModel):
    priority: str  # Low | Medium | High | Critical
    action: str
    rationale: str = ""

class PreventionResponse(BaseModel):
    recommendations: List[PreventiveRecommendation]
    generated_at: str = ""
