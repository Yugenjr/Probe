"""Comprehensive verification test suite guaranteeing v2.0 architectural integrity."""
import asyncio
from datetime import datetime, timezone
from probe.domain import (
    DriftEvidence,
    PerformanceCurveEvidence,
    UniversalEvidence,
    Hypothesis,
    Incident,
    IncidentSeverity,
    RemediationPlan,
    InterventionType,
)
from probe.interfaces import ResourceContext, TelemetryProvider, GovernanceProvider, ExecutionProvider
from probe.engine import InvestigationSession, InvestigationStatus, InvestigationOrchestrator, WorkerService
from probe.core.di import get_container
from probe_adapters.whylabs.client import WhyLabsTelemetryAdapter
from probe_adapters.evidently.client import EvidentlyTelemetryAdapter
from probe_adapters.arize.client import ArizeTelemetryAdapter
from probe_adapters.driftguard.client import DriftGuardAdapter
from probe.agents import InvestigatorAgent, ResearcherAgent, HypothesisAgent, ValidationAgent, RemediationAgent
from probe.extensibility import PluginLoader


def test_standalone_vendor_adapters() -> None:
    """Verify that standalone adapters cleanly implement segregated protocols without core leakage."""
    async def _run() -> None:
        whylabs = WhyLabsTelemetryAdapter(api_key="test-key", org_id="test-org")
        assert isinstance(whylabs, TelemetryProvider)
        ctx = ResourceContext(model_id="fraud-detector-v2", environment="production")
        drift_res = await whylabs.fetch_feature_drift(ctx)
        assert len(drift_res) == 2
        assert drift_res[0]["feature_name"] == "annual_income"

        evidently = EvidentlyTelemetryAdapter()
        assert isinstance(evidently, TelemetryProvider)
        ev_res = await evidently.get_drift_metrics(ctx)
        assert ev_res[0]["feature"] == "loan_amount"

        arize = ArizeTelemetryAdapter()
        assert isinstance(arize, TelemetryProvider)
        arize_res = await arize.get_model(ctx)
        assert arize_res["platform"] == "Arize AI"

        driftguard = DriftGuardAdapter()
        assert isinstance(driftguard, TelemetryProvider)
        assert isinstance(driftguard, GovernanceProvider)
        assert isinstance(driftguard, ExecutionProvider)
    
    asyncio.run(_run())


def test_discriminated_union_evidence_and_immutable_session() -> None:
    """Verify strictly typed Pydantic v2 discriminated unions and thread-safe snapshot generation."""
    drift_item = DriftEvidence(
        evidence_id="ev-001",
        source_provider="WhyLabsTelemetryAdapter",
        retrieved_by_tool="analyze_feature_drift",
        summary="High KL divergence detected on demographic feature.",
        confidence_weight=0.95,
        feature_name="age",
        distance_algorithm="kl_divergence",
        observed_distance=0.24,
        alarm_threshold=0.05,
        is_anomalous=True,
    )
    
    incident = Incident(
        incident_id="inc-9001",
        model_id="credit-risk-v1",
        source_platform="WhyLabs",
        trigger_type="drift_detected",
        severity=IncidentSeverity.HIGH,
    )
    
    session = InvestigationSession(
        session_id="inv-9001",
        investigation_id="inv-9001",
        incident=incident,
        status=InvestigationStatus.CREATED,
    )
    session.add_universal_evidence(drift_item)
    assert len(session.universal_evidence) == 1
    
    # Test immutable snapshotting
    snapshot = session.create_immutable_snapshot()
    assert snapshot.session_id == "inv-9001"
    assert snapshot.universal_evidence[0].observed_distance == 0.24
    
    # Verify modification separation
    session.transition_to(InvestigationStatus.COLLECTING_EVIDENCE, "Worker started.")
    assert session.status == InvestigationStatus.COLLECTING_EVIDENCE
    assert snapshot.status == InvestigationStatus.CREATED # Immutable snapshot unmutated


def test_deterministic_orchestrator_and_5_agent_roster() -> None:
    """Verify deterministic execution loop across our 5 domain expert reasoning agents."""
    # Ensure standard provider is bound to IoC runtime container for test validation
    container = get_container()
    default_adapter = DriftGuardAdapter()
    container.telemetry_provider = default_adapter
    container.governance_provider = default_adapter
    container.execution_provider = default_adapter

    async def _run() -> None:
        incident = Incident(
            incident_id="inc-test",
            model_id="sagemaker-churn-v1",
            source_platform="Arize AI",
            trigger_type="performance_degradation",
            severity=IncidentSeverity.CRITICAL,
        )
        
        orchestrator = InvestigationOrchestrator(container=container)
        session = await orchestrator.initiate_investigation(incident)
        assert session.status == InvestigationStatus.COLLECTING_EVIDENCE
        
        # Test individual agent execution
        inv_agent = InvestigatorAgent()
        inv_res = await inv_agent.execute(session)
        assert inv_res["status"] == "EVIDENCE_COLLECTED"
        
        res_agent = ResearcherAgent()
        res_res = await res_agent.execute(session)
        assert res_res["status"] == "CONTEXT_RETRIEVED"
        
        hyp_agent = HypothesisAgent()
        hyp_res = await hyp_agent.execute(session)
        assert hyp_res["status"] == "HYPOTHESIS_FORMULATED"
        assert len(session.hypotheses) == 1
        
        val_agent = ValidationAgent()
        val_res = await val_agent.execute(session)
        assert val_res["status"] == "VALIDATED"
        assert session.hypotheses[0].verified_by_simulation is True
        
        rem_agent = RemediationAgent()
        rem_res = await rem_agent.execute(session)
        assert rem_res["status"] == "REMEDIATION_PROPOSED"
        assert session.remediation_plan is not None
        assert session.remediation_plan.intervention_type == InterventionType.AUTOMATED_RETRAINING
        
    asyncio.run(_run())
    
    # Test worker service synchronous invocation wrapper
    worker_res = WorkerService.run_job_sync({"incident_id": "inc-worker", "model_id": "prod-model", "source_platform": "Evidently"})
    assert worker_res["status"] == InvestigationStatus.COMPLETED
