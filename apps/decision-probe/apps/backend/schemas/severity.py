from pydantic import BaseModel
from typing import List, Literal

class SeverityResponse(BaseModel):
    severity: Literal["SEV1", "SEV2", "SEV3", "SEV4"]
    impact_summary: str
    reasoning: List[str]
