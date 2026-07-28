from pydantic import BaseModel
from typing import List

class ValidationStep(BaseModel):
    action: str
    reason: str

class ValidationResponse(BaseModel):
    validation_plan: List[ValidationStep]
    missing_information: List[str]
    validation_summary: str
