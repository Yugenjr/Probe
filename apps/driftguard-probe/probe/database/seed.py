"""Database seeding utility generating enterprise mock data."""
import asyncio
import uuid
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .connection import async_session_factory
from .models.investigation import Investigation
from .models.timeline import TimelineEvent
from .models.agent import AgentExecution
from .models.evidence import EvidencePlanModel, EvidenceItemModel
from .models.mcp import McpServerMetadata, McpTool, McpExecution
from .models.report import HypothesisModel, EvaluationModel, ReportModel
from .models.knowledge import KnowledgeReference, InvestigationMemory
from .models.audit import AuditLog

logger = logging.getLogger("seed")


async def seed_data():
    """Seed target PostgreSQL database with sample incident records."""
    logger.info("[Seed] Beginning database seeding process...")
    
    async with async_session_factory() as session:
        # Check if already seeded
        query = select(Investigation).limit(1)
        res = await session.execute(query)
        if res.scalar_one_or_none():
            logger.info("[Seed] Database already contains records. Skipping seeding.")
            return

        session_id = "inv-demo-prod-01"
        started_at = datetime.utcnow() - timedelta(minutes=10)
        completed_at = datetime.utcnow()

        # 1. Add Investigation
        inv = Investigation(
            id=session_id,
            session_id=session_id,
            investigation_id=session_id,
            incident_id="inc-alert-9921",
            model_id="sagemaker-churn-v1",
            model_version="champion-v3",
            status="COMPLETED",
            priority="critical",
            started_at=started_at,
            completed_at=completed_at,
            duration_ms=600000,
            trigger_type="drift_detected",
            summary="Autonomous forensics correlated a 12% drift in user churn prediction features with high ADWIN alarms.",
            final_root_cause="Feature drift on user_payment_tenure feature due to demographic change.",
            confidence=0.92,
            raw_payload={"drift_score": 0.32, "metric": "ADWIN"},
            investigation_context={"predictions": [{"drift_score": 0.32}]}
        )
        session.add(inv)
        await session.flush()

        # 2. Add Timeline Events

        stages = [
            ("SupervisorStarted", "Supervisor", started_at),
            ("PlannerStarted", "Planner", started_at + timedelta(seconds=15)),
            ("EvidenceRequested", "EvidenceGateway", started_at + timedelta(seconds=30)),
            ("EvidenceReceived", "EvidenceGateway", started_at + timedelta(seconds=90)),
            ("HypothesisCreated", "Hypothesis", started_at + timedelta(seconds=150)),
            ("EvaluatorCompleted", "Evaluator", started_at + timedelta(seconds=240)),
            ("ReportGenerated", "Reporter", started_at + timedelta(seconds=300)),
            ("Completed", "Reporter", completed_at)
        ]
        for name, agent, ts in stages:
            session.add(TimelineEvent(
                investigation_id=session_id,
                event_type=name,
                stage=agent,
                timestamp=ts,
                duration_ms=12000,
                metadata_json={"agent": agent, "status": "completed"}
            ))

        # 3. Add Agent Executions
        agents = [
            ("Supervisor", started_at, started_at + timedelta(seconds=10), "llama-3.3-70b", 1200, 100),
            ("Planner", started_at + timedelta(seconds=15), started_at + timedelta(seconds=25), "llama-3.3-70b", 3400, 450),
            ("Investigator", started_at + timedelta(seconds=30), started_at + timedelta(seconds=80), "llama-3.3-70b", 5600, 890),
            ("Hypothesis", started_at + timedelta(seconds=150), started_at + timedelta(seconds=170), "llama-3.3-70b", 4200, 600)
        ]
        for name, start, finish, model, pt, ct in agents:
            session.add(AgentExecution(
                investigation_id=session_id,
                agent_name=name,
                started_at=start,
                finished_at=finish,
                latency_ms=int((finish - start).total_seconds() * 1000),
                prompt_version="v2.1",
                llm_model=model,
                prompt_tokens=pt,
                completion_tokens=ct,
                total_tokens=pt + ct,
                success=True,
                input_json={"context": "Telemetry data"},
                output_json={"observations": ["observed shift"]}
            ))

        # 4. Add MCP Servers & Tools
        servers = [
            ("knowledge", "local", ["runbooks", "knowledge_base"]),
            ("github", "http", ["code_history", "commits"]),
            ("mlflow", "process", ["experiment_traces", "runs"])
        ]
        for name, transport, caps in servers:
            session.add(McpServerMetadata(
                server_name=name,
                transport=transport,
                version="1.0.0",
                status="active",
                capabilities_json={"capabilities": caps},
                last_health_check=datetime.utcnow(),
                latency_ms=15
            ))

        # 5. Add Evidence Items
        evidences = [
            ("ev-01", "knowledge", "drift_stats", "runbooks", "search_runbooks", "Local runbook suggests retraining for churn drift signatures."),
            ("ev-02", "github", "code_change", "code_history", "search_commits", "Recent git commit c8e921a modified the preprocessing feature extraction threshold."),
            ("ev-03", "mlflow", "drift_stats", "experiment_traces", "search_runs", "MLflow run training statistics show drift on test demographic subsets.")
        ]
        for ev_id, provider, ev_type, cap, tool, summary in evidences:
            session.add(EvidenceItemModel(
                evidence_id=ev_id,
                investigation_id=session_id,
                source_provider=provider,
                evidence_type=ev_type,
                capability=cap,
                server=provider,
                tool=tool,
                transport="local" if provider == "knowledge" else "http",
                summary=summary,
                raw_json={"metric": "shift", "value": 0.32},
                confidence_weight=0.95
            ))

        # 6. Add Hypotheses
        session.add(HypothesisModel(
            hypothesis_id="hyp-01",
            investigation_id=session_id,
            title="demographic preprocessing shift",
            detailed_reasoning="Preprocessing changes in commit c8e921a filtered payment_tenure variables differently, causing covariate feature distribution variance.",
            supporting_evidence_ids=["ev-02", "ev-03"],
            likelihood_score=0.92,
            verified_by_simulation=True,
            weaknesses=["Requires production feature logs validation"],
            ranking=1
        ))

        # 7. Add Report
        session.add(ReportModel(
            report_id="rep-demo-01",
            investigation_id=session_id,
            primary_root_cause="demographic preprocessing shift",
            markdown_content="# Forensic Incident Report\n\n-Suspected Cause: pre-processing shift in commit c8e921a.",
            report_version="1.0.0"
        ))

        # 8. Add Audit log
        session.add(AuditLog(
            investigation_id=session_id,
            event_name="InvestigationClosed",
            actor="SupervisorAgent",
            details="Incident marked resolved. Forensics successfully saved to long-term memory."
        ))

        await session.commit()
        logger.info("[Seed] Database seeding completed successfully!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_data())
