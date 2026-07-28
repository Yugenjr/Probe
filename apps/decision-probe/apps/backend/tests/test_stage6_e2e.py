import os
import json
import logging
from fastapi.testclient import TestClient

# Mock the database engine for test
os.environ["TEST_DB"] = "1"
import storage.database
from sqlmodel import create_engine, SQLModel

test_engine = create_engine("sqlite:///e2e_stage6_test.db", connect_args={"check_same_thread": False})
storage.database.engine = test_engine

from main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure tables are created
SQLModel.metadata.drop_all(test_engine)
SQLModel.metadata.create_all(test_engine)

client = TestClient(app)

def test_stage6_e2e_pipeline():
    logger.info("Starting Stage 6 E2E Observability Integration Test")

    # 1. Create Workspace
    ws_response = client.post("/api/v1/workspaces", json={"title": "Stage 6 E2E Workspace", "initial_blocks": []})
    assert ws_response.status_code == 200
    workspace_id = ws_response.json()["id"]

    # 2. Add a mock base graph block to workspace (to verify fusion update capability)
    # The workspace router saves block "graph" during investigate. We can simulate creating a base graph block first.
    from storage.models import Block
    from sqlmodel import Session
    with Session(storage.database.engine) as session:
        base_graph_block = Block(
            workspace_id=workspace_id,
            type="graph",
            order=0,
            content={
                "nodes": [{"id": "node_existing", "type": "Document", "label": "Existing Log File"}],
                "edges": []
            }
        )
        session.add(base_graph_block)
        session.commit()

    # 3. Call POST /collect-evidence
    collect_response = client.post(f"/api/v1/workspaces/{workspace_id}/collect-evidence")
    assert collect_response.status_code == 200
    data = collect_response.json()

    # Verify response schema fields
    assert "logs" in data
    assert "metrics" in data
    assert "deployments" in data
    assert "git_changes" in data
    assert "fused_evidence" in data

    # Verify workspace block storage persistence
    get_ext = client.get(f"/api/v1/workspaces/{workspace_id}/external-evidence")
    assert get_ext.status_code == 200
    assert len(get_ext.json().get("logs", [])) >= 1

    get_changes = client.get(f"/api/v1/workspaces/{workspace_id}/changes")
    assert get_changes.status_code == 200
    assert len(get_changes.json().get("changes", [])) >= 1

    get_metrics = client.get(f"/api/v1/workspaces/{workspace_id}/metrics")
    assert get_metrics.status_code == 200
    assert len(get_metrics.json().get("metrics", [])) >= 1

    # 4. Verify graph updates are appended to base graph block
    with Session(storage.database.engine) as session:
        statement = session.query(Block).filter(Block.workspace_id == workspace_id, Block.type == "graph")
        graph_block = statement.first()
        assert graph_block is not None
        graph_content = graph_block.content
        
        # Check node updates (nodes: node_existing AND stage 6 collector nodes)
        nodes = graph_content.get("nodes", [])
        assert len(nodes) > 1
        node_ids = {n["id"] for n in nodes}
        assert "node_existing" in node_ids
        assert "node_payments_service" in node_ids

        # Check edge updates
        edges = graph_content.get("edges", [])
        assert len(edges) >= 3
        edge_types = {e["type"] for e in edges}
        assert "affected_service" in edge_types
        assert "correlated_with" in edge_types

    logger.info("Stage 6 E2E Observability Integration Test Passed Successfully!")
