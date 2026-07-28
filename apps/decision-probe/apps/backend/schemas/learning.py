from pydantic import BaseModel
from typing import List, Literal

class LearningRecommendationItem(BaseModel):
    type: Literal["investigation", "prevention"]
    suggestion: str

class LearningResponse(BaseModel):
    recommendations: List[LearningRecommendationItem]
