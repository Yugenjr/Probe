"""Comprehensive v3.0 architecture verification test suite proving Principal Staff design enhancements."""
import asyncio
import pytest
from datetime import datetime, timezone
from probe.domain.graph import EvidenceNode, EvidenceEdge, EdgeType, EvidenceGraph
from probe.engine import (
    ConfidenceEngine,
    HypothesisScoreMetric,
    EventType,
    StateDeltaEvent,
    EventSourcedSession,
    DCGWorkflowEngine,
    InvestigationSession,
    InvestigationStatus,
)
from probe.domain.incident import Incident, IncidentSeverity
from probe.extensibility import PluginPermissionManifest
from probe.agents import CausalSynthesisAgent, AdversarialCriticAgent, InterventionArchitectAgent
from probe.services import TelemetryCorrelationService, HistoricalRunbookMatcher, SimulationReplayEngine
from probe.core.di import get_container
from probe_adapters.driftguard.client import DriftGuardAdapter


def test_evidence_graph_causal_path_extraction() -> None:
    """Verify directed causal lineage traversal inside our EvidenceGraph architecture."""
    graph = EvidenceGraph(graph_id="graph-test-01")
    
    node1 = EvidenceNode(
        node_id="root-dataset-change",
        evidence_type="schema_shift",
        source_provider="WhyLabs",
        summary="Demographic column distribution altered upstream.",
        empirical_weight=0.90,
    )
    node2 = EvidenceNode(
        node_id="mid-feature-drift",
        evidence_type="feature_drift",
        source_provider="Evidently",
        summary="Wasserstein distance spiked to 0.28.",
        empirical_weight=0.88,
    )
    node3 = EvidenceNode(
        node_id="symptom-latency-spike",
        evidence_type="latency",
        source_provider="DriftGuard",
        summary="P99 latency jumped above SLA limit.",
        empirical_weight=0.95,
    )
    
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)
    
    graph.connect_nodes(node1.node_id, node2.node_id, EdgeType.CAUSAL_TO, "Upstream schema altered feature embedding.")
    graph.connect_nodes(node2.node_id, node3.node_id, EdgeType.CAUSAL_TO, "Embedding rebuild bottlenecks inference latency.")
    
    path = graph.extract_causal_path(node3.node_id)
    assert len(path) == 3
    assert path[0].node_id == "root-dataset-change"
    assert path[2].node_id == "symptom-latency-spike"


def test_algorithmic_confidence_engine_bayesian_calc() -> None:
    """Verify objective Bayesian hypothesis verification computation."""
    graph = EvidenceGraph(graph_id="graph-conf")
    n_supp = EvidenceNode(node_id="n1", evidence_type="test", source_provider="A", summary="ok", empirical_weight=0.90)
    n_contra = EvidenceNode(node_id="n2", evidence_type="test", source_provider="B", summary="bad", empirical_weight=0.10)
    graph.add_node(n_supp)
    graph.add_node(n_contra)
    
    score = ConfidenceEngine.evaluate_hypothesis(
        hypothesis_id="hyp-calc-1",
        supporting_node_ids=["n1"],
        contradiction_node_ids=["n2"],
        graph=graph,
        prior_similarity=0.75,
        sample_count=20000,
    )
    assert isinstance(score, HypothesisScoreMetric)
    assert 0.0 < score.computed_confidence <= 1.0
    assert score.empirical_support_score == 0.90


def test_event_sourced_journal_time_travel_replay() -> None:
    """Verify CQRS immutable append-only state delta logging and deterministic time-travel debug rehydration."""
    session = EventSourcedSession(session_id="es-9000")
    session.append_event(EventType.SESSION_INITIALIZED, {"target": "model-1"}, author="System")
    
    node_data = EvidenceNode(node_id="node-ev-1", evidence_type="drift", source_provider="WL", summary="drifted").model_dump(mode="json")
    session.append_event(EventType.EVIDENCE_NODE_ACCRUED, {"node_data": node_data}, author="Service")
    assert "node-ev-1" in session.materialized_graph.nodes
    
    # Commit third event
    session.append_event(EventType.REMEDIATION_DISPATCHED, {"status": "dispatched"}, author="InterventionArchitect")
    assert session.active_status == "COMPLETED"
    
    # Execute time-travel replay to sequence 2 (before remediation!)
    replayed = session.replay_to_sequence(target_sequence_id=2)
    assert "node-ev-1" in replayed.materialized_graph.nodes
    assert replayed.active_status == "COLLECTING_EVIDENCE" # Has not replayed remediation!
    assert len(replayed.export_audit_journal()) == 2


def test_dcg_cyclic_workflow_engine_and_feedback_loops() -> None:
    """Verify Directed Cyclic Graph workflow orchestration executing automated confidence refinement feedback loops."""
    async def _run() -> None:
        dcg = DCGWorkflowEngine(confidence_threshold=0.80, max_refinement_cycles=2)
        session = await dcg.execute_cyclic_investigation("session-dcg-01", {"model_id": "fraud-model", "trigger": "drift"})
        assert len(session.export_audit_journal()) >= 4
        assert len(session.materialized_graph.nodes) >= 2
    asyncio.run(_run())


def test_consolidated_3_agent_cognitive_roster() -> None:
    """Verify our consolidated 3-Agent Cognitive Reasoning Roster operating over DI and services."""
    container = get_container()
    default_adapter = DriftGuardAdapter()
    container.telemetry_provider = default_adapter
    container.governance_provider = default_adapter
    container.execution_provider = default_adapter
    
    async def _run() -> None:
        incident = Incident(
            incident_id="inc-v3",
            model_id="prod-classifier",
            source_platform="WhyLabs",
            trigger_type="drift_detected",
            severity=IncidentSeverity.CRITICAL,
        )
        session = InvestigationSession(
            session_id="inv-v3-test",
            investigation_id="inv-v3-test",
            incident=incident,
            status=InvestigationStatus.COLLECTING_EVIDENCE,
        )
        
        # Test deterministic correlation service replacing old IO agents
        graph = EvidenceGraph(graph_id="g-v3")
        svc_res = await TelemetryCorrelationService.extract_and_correlate("prod-classifier", graph)
        assert svc_res["nodes_added"] == 2
        
        # Test 3 pure cognitive agents
        causal_agent = CausalSynthesisAgent()
        causal_res = await causal_agent.execute(session)
        assert causal_res["status"] == "HYPOTHESIS_SYNTHESIZED"
        assert len(session.hypotheses) == 1
        
        critic_agent = AdversarialCriticAgent()
        critic_res = await critic_agent.execute(session)
        assert critic_res["status"] == "FALSIFICATION_EVALUATED"
        assert session.hypotheses[0].verified_by_simulation is True
        
        arch_agent = InterventionArchitectAgent()
        arch_res = await arch_agent.execute(session)
        assert arch_res["status"] == "REMEDIATION_DESIGNED"
        assert session.remediation_plan is not None
        assert session.remediation_plan.estimated_impact_percent > 0.0

    asyncio.run(_run())


def test_sandbox_plugin_manifest() -> None:
    """Verify out-of-process sandbox capability permission manifest definition."""
    manifest = PluginPermissionManifest(
        plugin_id="community-whylabs",
        executable_binary_path="/opt/plugins/whylabs_ipc_worker",
        allow_network_hosts=["api.whylabs.ai"],
        max_execution_timeout_seconds=10,
    )
    assert manifest.plugin_id == "community-whylabs"
    assert "api.whylabs.ai" in manifest.allow_network_hosts
