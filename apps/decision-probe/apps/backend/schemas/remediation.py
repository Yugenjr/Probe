from pydantic import BaseModel
from typing import List

class RemediationResponse(BaseModel):
    immediate_actions: List[str]
    permanent_fixes: List[str]
    prevention_steps: List[str]
    summary: str
