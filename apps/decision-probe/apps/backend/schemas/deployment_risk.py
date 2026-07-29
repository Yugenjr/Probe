from pydantic import BaseModel
from typing import List

class DeploymentRiskEntry(BaseModel):
    version: str
    risk: str  # Low | Medium | High | Critical
    reasons: List[str]

class DeploymentRiskResponse(BaseModel):
    deployments: List[DeploymentRiskEntry]
    generated_at: str = ""
