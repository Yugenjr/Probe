from pydantic import BaseModel
from typing import List, Literal

class ResolutionResponse(BaseModel):
    status: Literal["resolved", "monitoring", "open"]
    completed_actions: List[str]
    remaining_risks: List[str]
    summary: str = ""
