"""SQLAlchemy-backed repository managing investigation session entities."""
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository
from ..models.investigation import Investigation as DBInvestigation
from ..models.timeline import TimelineEvent as DBTimelineEvent
from ..models.agent import AgentExecution as DBAgentExecution
from ..models.evidence import EvidencePlanModel as DBEvidencePlan, EvidenceItemModel as DBEvidenceItem
from ..models.report import HypothesisModel as DBHypothesis, EvaluationModel as DBEvaluation, ReportModel as DBReport
from ..models.knowledge import KnowledgeReference as DBKnowledgeRef, InvestigationMemory as DBMemory
from ..models.audit import AuditLog as DBAuditLog

from ...engine.state import InvestigationSession, InvestigationStatus, AgentResult
from ...domain.incident import Incident, IncidentSeverity
from ...domain.evidence import DriftEvidence, RunbookReferenceEvidence, UniversalEvidence
from typing import Any
from ...domain.remediation import RemediationPlan
from ...context.models import InvestigationContext
from ...models.recommendation import EvaluationResult
from ...domain.hypothesis import CausalHypothesis

logger = logging.getLogger(__name__)


class InvestigationRepository(BaseRepository):
    """Manages transactional persistence for all investigation session aggregates."""

    async def save_session(self, session: InvestigationSession) -> None:
        """Atomically insert or update the investigation session and all associated child entities."""
        # 1. Check if investigation already exists
        query = select(DBInvestigation).where(DBInvestigation.session_id == session.session_id)
        res = await self.session.execute(query)
        db_inv = res.scalar_one_or_none()

        duration = None
        if session.completed_at:
            duration = int((session.completed_at - session.started_at).total_seconds() * 1000)

        raw_pay = dict(session.incident.raw_payload or {})
        raw_pay["execution_history"] = session.execution_history

        # Build investigation dict
        inv_data = {
            "session_id": session.session_id,
            "investigation_id": session.investigation_id,
            "incident_id": session.incident.incident_id,
            "model_id": session.incident.model_id,
            "model_version": session.incident.model_version or "latest",
            "status": session.status.value,
            "priority": session.incident.severity.value if session.incident.severity else "medium",
            "started_at": session.started_at.replace(tzinfo=None) if session.started_at else datetime.utcnow(),
            "completed_at": session.completed_at.replace(tzinfo=None) if session.completed_at else None,
            "duration_ms": duration,
            "trigger_type": session.incident.trigger_type or "drift_detected",
            "summary": getattr(session, "summary", ""),
            "final_root_cause": session.report.primary_root_cause if session.report else None,
            "confidence": session.evaluation_result.confidence if session.evaluation_result else 0.0,
            "raw_payload": raw_pay,
            "investigation_context": session.investigation_context.model_dump(mode="json") if session.investigation_context else None,
            "remediation_plan": session.remediation_plan.model_dump(mode="json") if session.remediation_plan else None,
        }


        if not db_inv:
            db_inv = DBInvestigation(id=session.session_id, **inv_data)
            self.session.add(db_inv)
            logger.debug("[InvestigationRepo] Creating new investigation record for %s", session.session_id)
        else:
            for key, val in inv_data.items():
                setattr(db_inv, key, val)
            logger.debug("[InvestigationRepo] Updating investigation record for %s", session.session_id)

        # 2. Save Evidence Plan
        if session.evidence_plan:
            plan_query = select(DBEvidencePlan).where(DBEvidencePlan.investigation_id == session.session_id)
            plan_res = await self.session.execute(plan_query)
            db_plan = plan_res.scalar_one_or_none()
            
            plan_data = {
                "goal": session.evidence_plan.goal,
                "capabilities_json": session.evidence_plan.model_dump(mode="json"),
            }
            if not db_plan:
                db_plan = DBEvidencePlan(investigation_id=session.session_id, **plan_data)
                self.session.add(db_plan)
            else:
                db_plan.goal = plan_data["goal"]
                db_plan.capabilities_json = plan_data["capabilities_json"]

        # 3. Save Evidence Items
        for item in session.universal_evidence:
            item_query = select(DBEvidenceItem).where(DBEvidenceItem.evidence_id == item.evidence_id)
            item_res = await self.session.execute(item_query)
            db_item = item_res.scalar_one_or_none()

            raw_json = item.model_dump(mode="json")
            item_data = {
                "source_provider": item.source_provider,
                "evidence_type": item.evidence_type,
                "capability": getattr(item, "capability", "unknown"),
                "server": getattr(item, "server", item.source_provider),
                "tool": getattr(item, "retrieved_by_tool", "unknown"),
                "transport": getattr(item, "transport", "local"),
                "summary": item.summary,
                "raw_json": raw_json,
                "confidence_weight": item.confidence_weight,
            }

            if not db_item:
                db_item = DBEvidenceItem(evidence_id=item.evidence_id, investigation_id=session.session_id, **item_data)
                self.session.add(db_item)
            else:
                for k, v in item_data.items():
                    setattr(db_item, k, v)

        # 4. Save Hypotheses
        for i, h in enumerate(session.hypotheses):
            h_id = h.hypothesis_id or f"hyp-{session.session_id}-{i}"
            h_query = select(DBHypothesis).where(DBHypothesis.hypothesis_id == h_id)
            h_res = await self.session.execute(h_query)
            db_h = h_res.scalar_one_or_none()

            h_data = {
                "title": getattr(h, "title", getattr(h, "primary_root_cause", "Hypothesis")),
                "detailed_reasoning": getattr(h, "detailed_reasoning", "\n".join(getattr(h, "causal_chain", []))),
                "supporting_evidence_ids": getattr(h, "supporting_evidence_ids", getattr(h, "supporting_evidence", [])),
                "likelihood_score": getattr(h, "likelihood_score", getattr(h, "confidence", 0.5)),
                "verified_by_simulation": getattr(h, "verified_by_simulation", False),
                "weaknesses": getattr(h, "weaknesses", getattr(h, "contradicting_evidence", [])),
                "ranking": i + 1,
            }

            if not db_h:
                db_h = DBHypothesis(hypothesis_id=h_id, investigation_id=session.session_id, **h_data)
                self.session.add(db_h)
            else:
                for k, v in h_data.items():
                    setattr(db_h, k, v)

        # 5. Save Report
        if session.report:
            rep_id = getattr(session.report, "report_id", f"rep-{session.session_id}")
            rep_query = select(DBReport).where(DBReport.report_id == rep_id)
            rep_res = await self.session.execute(rep_query)
            db_rep = rep_res.scalar_one_or_none()

            markdown_content = getattr(session.report, "markdown_content", str(session.report))
            rep_data = {
                "primary_root_cause": getattr(session.report, "primary_root_cause", "Feature drift"),
                "markdown_content": markdown_content,
                "html_content": getattr(session.report, "html_content", ""),
                "json_content": session.report.model_dump(mode="json") if hasattr(session.report, "model_dump") else {},
                "report_version": getattr(session.report, "report_version", "1.0.0"),
            }

            if not db_rep:
                db_rep = DBReport(report_id=rep_id, investigation_id=session.session_id, **rep_data)
                self.session.add(db_rep)
            else:
                for k, v in rep_data.items():
                    setattr(db_rep, k, v)

        # 6. Save Agent Execution results
        for res in session.agent_results:
            exec_query = select(DBAgentExecution).where(
                DBAgentExecution.investigation_id == session.session_id,
                DBAgentExecution.agent_name == res.agent_name
            )
            exec_res = await self.session.execute(exec_query)
            db_exec = exec_res.scalar_one_or_none()

            exec_data = {
                "started_at": res.started_at.replace(tzinfo=None) if res.started_at else datetime.utcnow(),
                "finished_at": res.finished_at.replace(tzinfo=None) if res.finished_at else datetime.utcnow(),
                "latency_ms": int(res.latency * 1000),
                "prompt_version": res.metadata.get("prompt_version", "v1"),
                "llm_model": res.metadata.get("model_name", "groq/llama-3.3"),
                "prompt_tokens": res.metadata.get("tokens_prompt", 0),
                "completion_tokens": res.metadata.get("tokens_completion", 0),
                "total_tokens": res.tokens,
                "success": res.success,
                "input_json": res.metadata.get("input_context", {}),
                "output_json": res.output if isinstance(res.output, dict) else {"content": str(res.output)},
                "error_message": res.metadata.get("error", None)
            }

            if not db_exec:
                db_exec = DBAgentExecution(investigation_id=session.session_id, agent_name=res.agent_name, **exec_data)
                self.session.add(db_exec)
            else:
                for k, v in exec_data.items():
                    setattr(db_exec, k, v)

        # 7. Add memory lookup entry if completed
        if session.status == InvestigationStatus.COMPLETED:
            mem_query = select(DBMemory).where(DBMemory.investigation_id == session.session_id)
            mem_res = await self.session.execute(mem_query)
            db_mem = mem_res.scalar_one_or_none()

            mem_data = {
                "model_id": session.incident.model_id,
                "problem_signature": f"Drift alert on {session.incident.model_id}. Status: {session.status.value}",
                "resolution": session.report.primary_root_cause if session.report else "Investigated",
                "confidence": session.evaluation_result.confidence if session.evaluation_result else 0.85,
                "evidence_ids": [ev.evidence_id for ev in session.universal_evidence],
                "runbooks_used": ["adwin-response-protocol"],
                "git_commit_hash": "N/A",
                "mlflow_run_id": "N/A",
                "outcome": "resolved",
            }

            if not db_mem:
                db_mem = DBMemory(investigation_id=session.session_id, **mem_data)
                self.session.add(db_mem)

        await self.session.flush()

    async def get_session(self, session_id: str) -> Optional[InvestigationSession]:
        """Load and reconstruct the complete domain aggregate session with all related sub-entities."""
        query = select(DBInvestigation).where(DBInvestigation.session_id == session_id)
        res = await self.session.execute(query)
        db_inv = res.scalar_one_or_none()
        if not db_inv:
            return None

        # Reconstruct Incident domain model
        severity = IncidentSeverity.MEDIUM
        try:
            severity = IncidentSeverity(db_inv.priority.upper())
        except ValueError:
            pass

        incident = Incident(
            incident_id=db_inv.incident_id,
            model_id=db_inv.model_id,
            trigger_type=db_inv.trigger_type,
            severity=severity,
            raw_payload=db_inv.raw_payload or {},
            model_version=db_inv.model_version
        )

        session = InvestigationSession(
            session_id=db_inv.session_id,
            investigation_id=db_inv.investigation_id,
            status=InvestigationStatus(db_inv.status.upper()),
            incident=incident,
            started_at=db_inv.started_at.replace(tzinfo=timezone.utc),
            updated_at=db_inv.updated_at.replace(tzinfo=timezone.utc),
            completed_at=db_inv.completed_at.replace(tzinfo=timezone.utc) if db_inv.completed_at else None,
            raw_payload=db_inv.raw_payload
        )
        session.execution_history = db_inv.raw_payload.get("execution_history", []) if db_inv.raw_payload else []


        if db_inv.investigation_context:
            session.investigation_context = InvestigationContext(**db_inv.investigation_context)
        if db_inv.remediation_plan:
            session.remediation_plan = RemediationPlan(**db_inv.remediation_plan)

        # Reconstruct Evidence Items
        ev_query = select(DBEvidenceItem).where(DBEvidenceItem.investigation_id == session_id)
        ev_res = await self.session.execute(ev_query)
        for row in ev_res.scalars():
            # Match domain subclasses
            if row.evidence_type == "runbook_reference":
                ev_obj = RunbookReferenceEvidence(
                    evidence_id=row.evidence_id,
                    source_provider=row.source_provider,
                    retrieved_by_tool=row.tool,
                    summary=row.summary,
                    confidence_weight=row.confidence_weight,
                    runbook_id=row.raw_json.get("runbook_id", "default"),
                    section_title=row.raw_json.get("section_title", ""),
                    recommended_actions=row.raw_json.get("recommended_actions", [])
                )
            else:
                ev_obj = DriftEvidence(
                    evidence_id=row.evidence_id,
                    source_provider=row.source_provider,
                    retrieved_by_tool=row.tool,
                    summary=row.summary,
                    confidence_weight=row.confidence_weight,
                    feature_name=row.raw_json.get("feature_name", "all_features"),
                    distance_algorithm=row.raw_json.get("distance_algorithm", "adwin"),
                    observed_distance=row.raw_json.get("observed_distance", 0.0),
                    alarm_threshold=row.raw_json.get("alarm_threshold", 0.15),
                    is_anomalous=row.raw_json.get("is_anomalous", True)
                )
            session.universal_evidence.append(ev_obj)

        # Reconstruct Hypotheses
        h_query = select(DBHypothesis).where(DBHypothesis.investigation_id == session_id).order_by(DBHypothesis.ranking)
        h_res = await self.session.execute(h_query)
        for row in h_res.scalars():
            session.hypotheses.append(
                CausalHypothesis(
                    hypothesis_id=row.hypothesis_id,
                    primary_root_cause=row.title or "Unknown root cause",
                    contributing_factors=[],
                    causal_chain=row.detailed_reasoning.split("\n") if row.detailed_reasoning else [],
                    supporting_evidence=row.supporting_evidence_ids or [],
                    contradicting_evidence=row.weaknesses or [],
                    confidence=row.likelihood_score or 0.5
                )
            )

        # Reconstruct Report
        rep_query = select(DBReport).where(DBReport.investigation_id == session_id)
        rep_res = await self.session.execute(rep_query)
        db_rep = rep_res.scalar_one_or_none()
        if db_rep:
            # Simple placeholder mock class mimicking domain report structure
            from pydantic import BaseModel
            class ReconstructedReport(BaseModel):
                primary_root_cause: str
                markdown_content: str
                report_version: str

            session.report = ReconstructedReport(
                primary_root_cause=db_rep.primary_root_cause,
                markdown_content=db_rep.markdown_content,
                report_version=db_rep.report_version
            )

        # Reconstruct Agent results
        exec_query = select(DBAgentExecution).where(DBAgentExecution.investigation_id == session_id)
        exec_res = await self.session.execute(exec_query)
        for row in exec_res.scalars():
            session.agent_results.append(
                AgentResult(
                    agent_name=row.agent_name,
                    started_at=row.started_at.replace(tzinfo=timezone.utc),
                    finished_at=row.finished_at.replace(tzinfo=timezone.utc),
                    success=row.success,
                    output=row.output_json,
                    latency=row.latency_ms / 1000.0,
                    tokens=row.total_tokens,
                    metadata={
                        "prompt_version": row.prompt_version,
                        "model_name": row.llm_model,
                        "tokens_prompt": row.prompt_tokens,
                        "tokens_completion": row.completion_tokens,
                        "error": row.error_message
                    }
                )
            )

        return session

    async def list_sessions(
        self,
        model_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[InvestigationSession]:
        """Filter, sort, search, and paginate investigation records for dashboard panels."""
        query = select(DBInvestigation.session_id).order_by(desc(DBInvestigation.started_at))
        if model_id:
            query = query.where(DBInvestigation.model_id == model_id)
        if status:
            query = query.where(DBInvestigation.status == status)

        query = query.limit(limit).offset(offset)
        res = await self.session.execute(query)
        session_ids = res.scalars().all()

        sessions = []
        for sid in session_ids:
            s = await self.get_session(sid)
            if s:
                sessions.append(s)
        return sessions

    async def add_timeline_event(self, session_id: str, event_type: str, stage: str, duration_ms: int = 0, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Record an atomic lifecycle stage transition event log."""
        db_event = DBTimelineEvent(
            investigation_id=session_id,
            event_type=event_type,
            stage=stage,
            duration_ms=duration_ms,
            metadata_json=metadata or {}
        )
        self.session.add(db_event)
        await self.session.flush()

    async def get_timeline_events(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieve fine-grained timeline history for dashboard progression logs."""
        query = select(DBTimelineEvent).where(DBTimelineEvent.investigation_id == session_id).order_by(DBTimelineEvent.timestamp)
        res = await self.session.execute(query)
        events = []
        for row in res.scalars():
            events.append({
                "id": row.id,
                "event_type": row.event_type,
                "stage": row.stage,
                "timestamp": row.timestamp.replace(tzinfo=timezone.utc).isoformat(),
                "duration_ms": row.duration_ms,
                "metadata": row.metadata_json
            })
        return events
