import os
import json
import logging
from fastapi.testclient import TestClient

# Mock the database engine for test
os.environ["TEST_DB"] = "1"
import storage.database
from sqlmodel import create_engine, SQLModel

test_engine = create_engine("sqlite:///e2e_stage7_test.db", connect_args={"check_same_thread": False})
storage.database.engine = test_engine

from main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure tables are created
SQLModel.metadata.drop_all(test_engine)
SQLModel.metadata.create_all(test_engine)

client = TestClient(app)

def test_stage7_e2e_pipeline():
    logger.info("Starting Stage 7 E2E Incident Orchestration Integration Test")

    # 1. Create Workspace
    ws_response = client.post("/api/v1/workspaces", json={"title": "Stage 7 E2E Workspace", "initial_blocks": []})
    assert ws_response.status_code == 200
    workspace_id = ws_response.json()["id"]

    # 2. Call POST /create-incident
    collect_response = client.post(f"/api/v1/workspaces/{workspace_id}/create-incident")
    assert collect_response.status_code == 200
    data = collect_response.json()

    # Verify response schema fields
    assert "incident" in data
    assert "severity" in data
    assert "response_plan" in data
    assert "communications" in data
    assert "resolution" in data

    # Verify workspace block storage persistence
    get_inc = client.get(f"/api/v1/workspaces/{workspace_id}/incident")
    assert get_inc.status_code == 200
    assert get_inc.json().get("incident_title") == "Payment Database Connection Failure"

    get_tasks = client.get(f"/api/v1/workspaces/{workspace_id}/tasks")
    assert get_tasks.status_code == 200
    assert len(get_tasks.json().get("tasks", [])) >= 1

    get_res = client.get(f"/api/v1/workspaces/{workspace_id}/resolution")
    assert get_res.status_code == 200
    assert get_res.json().get("status") == "monitoring"

    get_kn = client.get(f"/api/v1/workspaces/{workspace_id}/knowledge")
    assert get_kn.status_code == 200
    assert "problem" in get_kn.json()

    logger.info("Stage 7 E2E Incident Orchestration Integration Test Passed Successfully!")
