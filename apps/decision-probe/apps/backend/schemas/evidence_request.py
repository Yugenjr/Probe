from pydantic import BaseModel
from typing import List, Literal

class EvidenceRequestItem(BaseModel):
    type: Literal["log", "metric", "config", "trace"]
    source: str
    query: str
    time_range: str

class EvidenceRequestResponse(BaseModel):
    requests: List[EvidenceRequestItem]
