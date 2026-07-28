import time
import io
import os
import json
import logging
from fastapi.testclient import TestClient

# Mock the database engine for test
os.environ["TEST_DB"] = "1"
import storage.database
from sqlmodel import create_engine, SQLModel

test_engine = create_engine("sqlite:///e2e_stage2_test.db", connect_args={"check_same_thread": False})
storage.database.engine = test_engine

from main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure tables are created
SQLModel.metadata.drop_all(test_engine)
SQLModel.metadata.create_all(test_engine)

client = TestClient(app)

def test_stage2_e2e_pipeline():
    logger.info("Starting Stage 2 E2E Integration Pipeline Test")

    # 1. Create Workspace
    ws_response = client.post("/api/v1/workspaces", json={"title": "Stage 2 Test Workspace", "initial_blocks": []})
    assert ws_response.status_code == 200
    ws_data = ws_response.json()
    workspace_id = ws_data["id"]

    # 2. Upload log file containing timestamped logs
    log_content = (
        "2026-07-24 10:40:00 [payments] Deployment of payments v1.1.0 succeeded.\n"
        "2026-07-24 10:41:12 [payments] ERROR: Connection failed to postgresql database.\n"
    )
    file_data = {"file": ("payments_test.log", io.BytesIO(log_content.encode("utf-8")), "text/plain")}
    upload_response = client.post(f"/api/v1/workspaces/{workspace_id}/upload", files=file_data)
    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    doc_id = upload_data["id"]

    # 3. Poll indexing status
    indexed = False
    for _ in range(10):
        status_response = client.get(f"/api/v1/workspaces/{workspace_id}/status")
        assert status_response.status_code == 200
        status_data = status_response.json()
        if status_data.get("all_indexed"):
            indexed = True
            break
        time.sleep(0.5)
    
    assert indexed, "Background document processing timed out"

    # 4. POST investigate to trigger the full pipeline
    goal = "Investigate the payments service connection failures"
    investigate_response = client.post(f"/api/v1/workspaces/{workspace_id}/investigate", json={"goal": goal})
    assert investigate_response.status_code == 200
    res_data = investigate_response.json()

    # Validate output schema
    assert "plan" in res_data
    assert "timeline" in res_data
    assert "evidence" in res_data
    assert "graph" in res_data

    # Validate timeline ordering & details
    timeline = res_data["timeline"]
    events = timeline.get("events", [])
    assert len(events) == 2
    # Verify chronological sorting (10:40:00 -> 10:41:12)
    assert events[0]["timestamp"] == "2026-07-24T10:40:00Z"
    assert events[1]["timestamp"] == "2026-07-24T10:41:12Z"
    assert events[0]["service"] == "payments"
    assert events[1]["service"] == "payments"
    assert "postgresql" in events[1]["description"].lower()

    # Validate evidence entities list
    evidence = res_data["evidence"]
    entities = evidence.get("entities", [])
    entity_names = {e["name"].lower() for e in entities}
    assert "payments" in entity_names
    assert "postgresql" in entity_names

    # Validate graph structure
    graph = res_data["graph"]
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    assert len(nodes) >= 2
    
    # 5. Verify database persistence via GET endpoints
    # Get Timeline
    get_timeline = client.get(f"/api/v1/workspaces/{workspace_id}/timeline")
    assert get_timeline.status_code == 200
    assert len(get_timeline.json().get("events", [])) == 2

    # Get Evidence
    get_evidence = client.get(f"/api/v1/workspaces/{workspace_id}/evidence")
    assert get_evidence.status_code == 200
    assert len(get_evidence.json().get("entities", [])) == len(entities)

    # Get Graph
    get_graph = client.get(f"/api/v1/workspaces/{workspace_id}/graph")
    assert get_graph.status_code == 200
    assert len(get_graph.json().get("nodes", [])) == len(nodes)

    logger.info("Stage 2 E2E Integration Pipeline Test Passed Successfully!")
