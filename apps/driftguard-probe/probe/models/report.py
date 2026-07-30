"""Investigation report domain model."""
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field
from .incident import Incident
from .evidence import EvidenceItem
from typing import Any
from .recommendation import Recommendation
from .experiment import Experiment


class InvestigationReport(BaseModel):
    """Complete executive diagnostic report synthesizing all findings."""
    report_id: str = Field(..., description="Unique generated report identifier")
    investigation_id: str = Field(..., description="Corresponding execution state ID")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    incident_summary: Incident
    primary_root_cause: str = Field(..., description="High-confidence consensus explanation of degradation")
    supporting_evidence: List[EvidenceItem] = Field(default_factory=list)
    tested_hypotheses: List[Any] = Field(default_factory=list)
    experiments: List[Experiment] = Field(default_factory=list)
    recommended_action: Optional[Recommendation] = None
    markdown_content: str = Field(default="", description="Rendered human-readable report format")

    # TODO: Implementation pending for markdown rendering engine and PDF export formatting
