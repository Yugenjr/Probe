"""Universal resource routing designator accommodating multi-tenant enterprise monitoring platforms."""
from typing import Optional
from pydantic import BaseModel, Field


class ResourceContext(BaseModel):
    """Compound identifier supporting routing across single-tenant, multi-org, and cloud deployments.
    
    Supersedes primitive string model IDs to allow seamless operation across AWS Sagemaker ARNs,
    WhyLabs dataset profiles, Arize AI monitor workspaces, and DriftGuard installations.
    """
    workspace_id: Optional[str] = Field(default=None, description="Enterprise tenant or workspace identifier")
    org_id: Optional[str] = Field(default=None, description="Organization or division designator")
    model_id: str = Field(..., description="Target machine learning deployment ID or dataset name")
    environment: str = Field(default="production", description="Runtime deployment stage e.g. 'staging' or 'production'")
    monitor_id: Optional[str] = Field(default=None, description="Originating monitor or diagnostic profile ID")
