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

test_engine = create_engine("sqlite:///e2e_stage5_test.db", connect_args={"check_same_thread": False})
storage.database.engine = test_engine

from main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure tables are created
SQLModel.metadata.drop_all(test_engine)
SQLModel.metadata.create_all(test_engine)

client = TestClient(app)

def test_stage5_e2e_pipeline():
    logger.info("Starting Stage 5 E2E Autonomous Loop Test")

    # 1. Create Workspace
    ws_response = client.post("/api/v1/workspaces", json={"title": "Stage 5 Loop Workspace", "initial_blocks": []})
    assert ws_response.status_code == 200
    workspace_id = ws_response.json()["id"]

    # 2. Upload the first log file (Initial context)
    log_content_1 = "2026-07-24 10:41:12 [payments] ERROR: PostgreSQL exceeded connection limit."
    file_data_1 = {"file": ("payments.log", io.BytesIO(log_content_1.encode("utf-8")), "text/plain")}
    upload_res_1 = client.post(f"/api/v1/workspaces/{workspace_id}/upload", files=file_data_1)
    assert upload_res_1.status_code == 200

    # Poll status until indexed
    indexed = False
    for _ in range(10):
        status_res = client.get(f"/api/v1/workspaces/{workspace_id}/status")
        if status_res.json().get("all_indexed"):
            indexed = True
            break
        time.sleep(0.5)
    assert indexed, "Initial file indexing timed out"

    # 3. Call Investigate (Iteration 1)
    investigate_res_1 = client.post(f"/api/v1/workspaces/{workspace_id}/investigate", json={"goal": "Investigate connection errors"})
    assert investigate_res_1.status_code == 200
    res_data_1 = investigate_res_1.json()

    # Validate output has loop blocks
    assert "evidence_gap" in res_data_1
    assert "evidence_requests" in res_data_1
    assert "investigation_iterations" in res_data_1

    # Check Iteration 1 state (Confidence should be 0.75, waiting_for_evidence)
    iterations_1 = res_data_1["investigation_iterations"].get("iterations", [])
    assert len(iterations_1) == 1
    assert iterations_1[0]["iteration"] == 1
    assert iterations_1[0]["status"] == "waiting_for_evidence"
    assert iterations_1[0]["confidence_change"]["after"] == 0.75

    # 4. Upload second file (Simulating evidence acquisition: config parameters)
    log_content_2 = "2026-07-24 10:40:00 [payments] Configured max_connections database limit = 100."
    file_data_2 = {"file": ("postgres_config.log", io.BytesIO(log_content_2.encode("utf-8")), "text/plain")}
    upload_res_2 = client.post(f"/api/v1/workspaces/{workspace_id}/upload", files=file_data_2)
    assert upload_res_2.status_code == 200

    # Poll status until indexed
    indexed = False
    for _ in range(10):
        status_res = client.get(f"/api/v1/workspaces/{workspace_id}/status")
        if status_res.json().get("all_indexed"):
            indexed = True
            break
        time.sleep(0.5)
    assert indexed, "Second file indexing timed out"

    # 5. Call Investigate again (Iteration 2)
    investigate_res_2 = client.post(f"/api/v1/workspaces/{workspace_id}/investigate", json={"goal": "Investigate connection errors"})
    assert investigate_res_2.status_code == 200
    res_data_2 = investigate_res_2.json()

    # Check Iteration 2 state (Confidence should improve to 0.88, status completed)
    iterations_2 = res_data_2["investigation_iterations"].get("iterations", [])
    assert len(iterations_2) == 2
    assert iterations_2[1]["iteration"] == 2
    assert iterations_2[1]["status"] == "completed"
    assert iterations_2[1]["confidence_change"]["before"] == 0.75
    assert iterations_2[1]["confidence_change"]["after"] == 0.88

    # 6. Verify block persistence via endpoints
    # Get Evidence Gaps
    get_gaps = client.get(f"/api/v1/workspaces/{workspace_id}/evidence-gaps")
    assert get_gaps.status_code == 200
    assert "evidence_gaps" in get_gaps.json()

    # Get Evidence Requests
    get_reqs = client.get(f"/api/v1/workspaces/{workspace_id}/evidence-requests")
    assert get_reqs.status_code == 200
    assert "requests" in get_reqs.json()

    # Get Iterations list
    get_iters = client.get(f"/api/v1/workspaces/{workspace_id}/iterations")
    assert get_iters.status_code == 200
    assert len(get_iters.json().get("iterations", [])) == 2

    logger.info("Stage 5 E2E Autonomous Loop Test Passed Successfully!")
