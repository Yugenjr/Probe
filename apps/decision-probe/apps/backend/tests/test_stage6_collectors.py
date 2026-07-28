import pytest
from services.external.log_collector_agent import LogCollectorAgent
from services.external.metrics_collector_agent import MetricsCollectorAgent
from services.external.deployment_collector_agent import DeploymentCollectorAgent
from services.external.git_change_agent import GitChangeAgent
from services.evidence_fusion_agent import EvidenceFusionAgent

@pytest.mark.asyncio
async def test_log_collector():
    collector = LogCollectorAgent()
    raw = await collector.fetch("payments", "last_hour")
    normalized = collector.normalize(raw)
    
    assert "logs" in normalized
    assert len(normalized["logs"]) >= 1
    assert normalized["logs"][0]["service"] == "payments"
    assert collector.validate(normalized) is True

@pytest.mark.asyncio
async def test_metrics_collector():
    collector = MetricsCollectorAgent()
    raw = await collector.fetch("payments", "last_hour")
    normalized = collector.normalize(raw)
    
    assert "metrics" in normalized
    assert len(normalized["metrics"]) >= 1
    assert normalized["metrics"][0]["name"] == "cpu_usage"
    assert collector.validate(normalized) is True

@pytest.mark.asyncio
async def test_deployment_collector():
    collector = DeploymentCollectorAgent()
    raw = await collector.fetch("last_hour")
    normalized = collector.normalize(raw)
    
    assert "changes" in normalized
    assert len(normalized["changes"]) >= 1
    assert normalized["changes"][0]["service"] == "payments"
    assert collector.validate(normalized) is True

@pytest.mark.asyncio
async def test_git_collector():
    collector = GitChangeAgent()
    raw = await collector.fetch()
    normalized = collector.normalize(raw)
    
    assert "commits" in normalized
    assert len(normalized["commits"]) >= 1
    assert "apps/payments/" in normalized["commits"][0]["files_changed"][0]
    assert collector.validate(normalized) is True

@pytest.mark.asyncio
async def test_evidence_fusion_agent():
    agent = EvidenceFusionAgent()
    
    logs = {"logs": [{"timestamp": "2026-07-24T10:41:12Z", "service": "payments", "level": "ERROR", "message": "out of pool"}]}
    metrics = {"metrics": [{"name": "db_connections", "value": 98, "timestamp": "2026-07-24T10:41:12Z"}]}
    deploys = {"changes": [{"service": "payments", "version": "v1.1.0", "changed_at": "2026-07-24T10:40:00Z", "author": "alex", "summary": "updated pool config"}]}
    git_changes = {"commits": [{"hash": "a4f8d29b", "author": "alex", "message": "optimized pools", "files_changed": ["database.ts"]}]}

    fused = await agent.fuse_evidence([], logs, metrics, deploys, git_changes)
    
    assert "new_evidence_chunks" in fused
    assert len(fused["new_evidence_chunks"]) >= 4
    assert fused["new_evidence_chunks"][0]["relevance_score"] > 0.0
    
    assert "graph_updates" in fused
    assert len(fused["graph_updates"]) == 1
    
    graph_update = fused["graph_updates"][0]
    assert "nodes" in graph_update
    assert "edges" in graph_update
    
    # Assert Node types are extended appropriately
    node_types = {n["type"] for n in graph_update["nodes"]}
    assert "Service" in node_types
    assert "Deployment" in node_types
    assert "Commit" in node_types
    assert "Metric" in node_types
    
    # Assert Edge types are extended appropriately
    edge_types = {e["type"] for e in graph_update["edges"]}
    assert "affected_service" in edge_types
    assert "deployed_before" in edge_types
    assert "correlated_with" in edge_types
