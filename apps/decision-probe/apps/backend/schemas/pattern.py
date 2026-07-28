from pydantic import BaseModel
from typing import List

class FailurePatternItem(BaseModel):
    pattern: str
    occurrences: int
    affected_services: List[str]

class PatternResponse(BaseModel):
    patterns: List[FailurePatternItem]
