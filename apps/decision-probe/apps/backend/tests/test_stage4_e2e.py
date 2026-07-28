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

test_engine = create_engine("sqlite:///e2e_stage4_test.db", connect_args={"check_same_thread": False})
storage.database.engine = test_engine

from main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure tables are created
SQLModel.metadata.drop_all(test_engine)
SQLModel.metadata.create_all(test_engine)

client = TestClient(app)

def test_stage4_e2e_pipeline():
    logger.info("Starting Stage 4 E2E Integration Pipeline Test")

    # 1. Create Workspace
    ws_response = client.post("/api/v1/workspaces", json={"title": "Stage 4 Test Workspace", "initial_blocks": []})
    assert ws_response.status_code == 200
    ws_data = ws_response.json()
    workspace_id = ws_data["id"]

    # 2. Upload log file containing timestamped logs
    log_content = (
        "2026-07-24 10:40:00 [payments] Deployment of payments v1.1.0 succeeded.\n"
        "2026-07-24 10:41:12 [payments] ERROR: Connection failed to postgresql database.\n"
    )
    file_data = {"file": ("payments_stage4.log", io.BytesIO(log_content.encode("utf-8")), "text/plain")}
    upload_response = client.post(f"/api/v1/workspaces/{workspace_id}/upload", files=file_data)
    assert upload_response.status_code == 200

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
    
    assert indexed, "Background processing timed out"

    # 4. POST investigate to trigger the full pipeline
    goal = "Verify payments service connection database limits exhaustion"
    investigate_response = client.post(f"/api/v1/workspaces/{workspace_id}/investigate", json={"goal": goal})
    assert investigate_response.status_code == 200
    res_data = investigate_response.json()

    # Validate output schema components
    assert "plan" in res_data
    assert "timeline" in res_data
    assert "evidence" in res_data
    assert "graph" in res_data
    assert "hypotheses" in res_data
    assert "review" in res_data
    assert "root_cause" in res_data
    assert "validation" in res_data
    assert "remediation" in res_data

    # Validate validation details
    validation = res_data["validation"]
    assert "validation_plan" in validation
    assert len(validation["validation_plan"]) >= 1
    assert "missing_information" in validation
    assert "validation_summary" in validation

    # Validate remediation details
    remediation = res_data["remediation"]
    assert "immediate_actions" in remediation
    assert len(remediation["immediate_actions"]) >= 1
    assert "permanent_fixes" in remediation
    assert "prevention_steps" in remediation
    assert "summary" in remediation

    # 5. Verify database persistence via GET endpoints
    # Get Validation
    get_val = client.get(f"/api/v1/workspaces/{workspace_id}/validation")
    assert get_val.status_code == 200
    assert len(get_val.json().get("validation_plan", [])) == len(validation["validation_plan"])

    # Get Remediation
    get_rem = client.get(f"/api/v1/workspaces/{workspace_id}/remediation")
    assert get_rem.status_code == 200
    assert len(get_rem.json().get("immediate_actions", [])) == len(remediation["immediate_actions"])

    logger.info("Stage 4 E2E Integration Pipeline Test Passed Successfully!")
