from pydantic import BaseModel
from typing import List, Literal

class EvidenceGapItem(BaseModel):
    gap: str
    importance: Literal["high", "medium", "low"]
    required_source: str
    reason: str

class EvidenceGapResponse(BaseModel):
    evidence_gaps: List[EvidenceGapItem]
    should_continue: bool
