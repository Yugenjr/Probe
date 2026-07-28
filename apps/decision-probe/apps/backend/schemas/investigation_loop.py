from pydantic import BaseModel
from typing import Literal

class ConfidenceChange(BaseModel):
    before: float
    after: float

class InvestigationIterationItem(BaseModel):
    iteration: int
    status: Literal["completed", "waiting_for_evidence", "insufficient"]
    confidence_change: ConfidenceChange
    reason: str
