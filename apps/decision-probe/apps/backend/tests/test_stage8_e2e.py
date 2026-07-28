import os
import json
import logging
from fastapi.testclient import TestClient

# Mock the database engine for test
os.environ["TEST_DB"] = "1"
import storage.database
from sqlmodel import create_engine, SQLModel

test_engine = create_engine("sqlite:///e2e_stage8_test.db", connect_args={"check_same_thread": False})
storage.database.engine = test_engine

from main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure tables are created
SQLModel.metadata.drop_all(test_engine)
SQLModel.metadata.create_all(test_engine)

client = TestClient(app)

def test_stage8_e2e_pipeline():
    logger.info("Starting Stage 8 E2E Self-Learning Integration Test")

    # 1. Create Workspace
    ws_response = client.post("/api/v1/workspaces", json={"title": "Stage 8 E2E Workspace", "initial_blocks": []})
    assert ws_response.status_code == 200
    workspace_id = ws_response.json()["id"]

    # 2. Call POST /learn
    learn_response = client.post(f"/api/v1/workspaces/{workspace_id}/learn")
    assert learn_response.status_code == 200
    data = learn_response.json()

    # Verify response schema fields
    assert "similar_incidents" in data
    assert "patterns" in data
    assert "recommendations" in data

    # Verify workspace block storage persistence
    get_sim = client.get(f"/api/v1/workspaces/{workspace_id}/similar-incidents")
    assert get_sim.status_code == 200
    assert len(get_sim.json().get("similar_incidents", [])) >= 1

    get_recs = client.get(f"/api/v1/workspaces/{workspace_id}/recommendations")
    assert get_recs.status_code == 200
    assert len(get_recs.json().get("recommendations", [])) >= 1

    get_pat = client.get(f"/api/v1/workspaces/{workspace_id}/patterns")
    assert get_pat.status_code == 200
    assert len(get_pat.json().get("patterns", [])) == 1

    logger.info("Stage 8 E2E Self-Learning Integration Test Passed Successfully!")
