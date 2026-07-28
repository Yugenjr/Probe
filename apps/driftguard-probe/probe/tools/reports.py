"""Diagnostic reporting compilation tool."""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict
from .base import BaseTool


class GenerateReportTool(BaseTool):
    """Tool compiling executive-ready diagnostic markdown reports from accrued investigation state."""
    @property
    def name(self) -> str:
        return "generate_report"

    @property
    def description(self) -> str:
        return "Synthesize tested hypotheses and evidence items into a formatted executive summary report."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "investigation_id": {"type": "string"},
                "root_cause_summary": {"type": "string"},
            },
            "required": ["investigation_id", "root_cause_summary"],
        }

    async def invoke(self, **kwargs: Any) -> Dict[str, Any]:
        inv_id = kwargs.get("investigation_id", "inv-default")
        rc_summary = kwargs.get("root_cause_summary", "Anomaly detected.")
        markdown = (
            f"# Automated Investigation Report: {inv_id}\n\n"
            f"**Generated:** {datetime.now(timezone.utc).isoformat()}\n\n"
            f"## Primary Root Cause\n{rc_summary}\n\n"
            f"*Report compiled autonomously via DriftGuard Probe.*"
        )
        return {"report_id": f"rep-{uuid.uuid4().hex[:6]}", "markdown": markdown, "status": "PUBLISHED"}
