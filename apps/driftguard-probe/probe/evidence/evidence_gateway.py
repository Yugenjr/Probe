"""EvidenceGateway collecting evidence across Knowledge, GitHub, and MLflow MCP sources.

The Investigator Agent queries only this gateway, decoupling the agent from
the specific MCP tools, servers, and transport implementations.
"""
import logging
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..mcp.gateway.tool_gateway import ToolGateway
from ..mcp.types import ToolResult
from ..engine.state import InvestigationSession
from ..domain.evidence import DriftEvidence, RunbookReferenceEvidence

logger = logging.getLogger(__name__)


class EvidenceItem(BaseModel):
    source: str = Field(..., description="Name of the server source (knowledge, github, mlflow)")
    tool: str = Field(..., description="Tool name executed")
    elapsed_ms: int = Field(..., description="Time taken for execution")
    success: bool = Field(..., description="Whether execution succeeded")
    content: str = Field(..., description="Result content")


class EvidenceBundle(BaseModel):
    """Aggregated evidence sources queried during planning/investigation prep."""
    session_id: str
    items: List[EvidenceItem] = Field(default_factory=list)
    combined_context: str = Field(default="", description="Merged textual context for LLM ingestion")


class EvidenceGateway:
    """Consolidated gateway mediating between Probe agents and MCP servers.

    Gathers knowledge base documents, code/commit context from GitHub, and MLflow traces.
    """

    def __init__(self, tool_gateway: ToolGateway) -> None:
        self._tool_gateway = tool_gateway
        self._mcp_activity_log: List[Dict[str, Any]] = []

    def get_activity_log(self) -> List[Dict[str, Any]]:
        """Return audit trail of all executed MCP calls."""
        return self._mcp_activity_log

    async def collect_evidence(self, session: InvestigationSession) -> EvidenceBundle:
        """Gathers relevant evidence from connected MCP sources based on Planner's EvidencePlan.

        Args:
            session: The active InvestigationSession containing the incident and optional evidence_plan.

        Returns:
            EvidenceBundle containing all retrieved details and integrated LLM context.
        """
        model_id = session.incident.model_id if session.incident else "unknown"
        drift_score = 0.25
        if session.incident and session.incident.raw_payload:
            drift_score = session.incident.raw_payload.get("drift_score", 0.25)
        if drift_score is None:
            drift_score = 0.25


        bundle = EvidenceBundle(session_id=session.session_id)
        context_blocks = []

        # List servers currently registered in the registry
        registered_servers = self._tool_gateway.list_servers()
        logger.info("[EvidenceGateway] Active MCP Sources: %s", registered_servers)

        from ..core.di import get_container
        registry = get_container().capability_registry

        # Resolve plan or build a default one
        plan = session.evidence_plan
        if not plan:
            # Construct a default fallback plan
            from ..mcp.capability import EvidencePlan, CapabilityRequest
            plan = EvidencePlan(
                goal="Default diagnostic collection",
                capabilities=[
                    CapabilityRequest(capability="runbooks", priority=1, required=True),
                    CapabilityRequest(capability="code_history", priority=2, required=False),
                    CapabilityRequest(capability="experiment_traces", priority=3, required=False),
                ]
            )

        for req in plan.capabilities:
            targets = registry.resolve(req.capability)
            if not targets:
                logger.warning("[EvidenceGateway] Capability '%s' is not registered in CapabilityRegistry", req.capability)
                req.status = "failed"
                continue

            for server, tool in targets:
                if server not in registered_servers:
                    logger.debug("[EvidenceGateway] Server '%s' for capability '%s' is not active/registered", server, req.capability)
                    continue

                start = time.perf_counter()
                try:
                    # Construct default arguments for execution
                    arguments = {}
                    if tool == "search_runbooks" or tool == "search_documents":
                        arguments = {"query": f"{model_id} drift score {drift_score:.2f}", "limit": 2}
                    elif tool == "search_code" or tool == "search_commits":
                        arguments = {"query": f"model_id = '{model_id}'", "limit": 2}
                    elif tool == "search_traces" or tool == "search_runs":
                        arguments = {"filter_string": f"tags.model_id = '{model_id}'", "limit": 2}

                    res = await self._tool_gateway.execute(
                        server=server,
                        tool=tool,
                        arguments=arguments
                    )
                    elapsed = int((time.perf_counter() - start) * 1000)
                    success = res.success
                    content = res.content if success else f"Error: {res.error}"

                    bundle.items.append(
                        EvidenceItem(source=server, tool=tool, elapsed_ms=elapsed, success=success, content=content)
                    )
                    self._record_activity(server, tool, elapsed, success)
                    req.status = "completed" if success else "failed"

                    if success and res.content:
                        context_blocks.append(f"=== {server.capitalize()} ({req.capability}) ===\n{res.content}")
                        if server == "knowledge":
                            # Attach standard runbook reference evidence to session if found
                            runbook_ev = RunbookReferenceEvidence(
                                evidence_id="ev-kb-runbook",
                                source_provider="KnowledgeBase",
                                retrieved_by_tool=tool,
                                summary="Retrieved relevant playbooks and guidelines matching the current incident signature.",
                                runbook_id="adwin-response-protocol",
                                section_title="ADWIN Drift Response Protocol",
                                recommended_actions=["Monitor feature drift", "Trigger model retraining if accuracy drops"]
                            )
                            session.add_universal_evidence(runbook_ev)
                except Exception as e:
                    logger.error("[EvidenceGateway] Failed querying capability '%s' on %s/%s: %s", req.capability, server, tool, e)
                    req.status = "failed"

        bundle.combined_context = "\n\n".join(context_blocks)
        return bundle


    def _record_activity(self, server: str, tool: str, duration: int, success: bool) -> None:
        self._mcp_activity_log.append({
            "timestamp": time.time(),
            "server": server,
            "tool": tool,
            "duration_ms": duration,
            "success": success
        })
