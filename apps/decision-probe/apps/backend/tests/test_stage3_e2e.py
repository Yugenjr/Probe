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

test_engine = create_engine("sqlite:///e2e_stage3_test.db", connect_args={"check_same_thread": False})
storage.database.engine = test_engine

from main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure tables are created
SQLModel.metadata.drop_all(test_engine)
SQLModel.metadata.create_all(test_engine)

client = TestClient(app)

def test_stage3_e2e_pipeline():
    logger.info("Starting Stage 3 E2E Integration Pipeline Test")

    # 1. Create Workspace
    ws_response = client.post("/api/v1/workspaces", json={"title": "Stage 3 Test Workspace", "initial_blocks": []})
    assert ws_response.status_code == 200
    ws_data = ws_response.json()
    workspace_id = ws_data["id"]

    # 2. Upload log file containing timestamped logs
    log_content = (
        "2026-07-24 10:40:00 [payments] Deployment of payments v1.1.0 succeeded.\n"
        "2026-07-24 10:41:12 [payments] ERROR: Connection failed to postgresql database.\n"
    )
    file_data = {"file": ("payments_stage3.log", io.BytesIO(log_content.encode("utf-8")), "text/plain")}
    upload_response = client.post(f"/api/v1/workspaces/{workspace_id}/upload", files=file_data)
    assert upload_response.status_code == 200
    upload_data = upload_response.json()

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
    goal = "Investigate payment timeouts and db outages"
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

    # Validate hypotheses listing
    hypotheses = res_data["hypotheses"].get("hypotheses", [])
    assert len(hypotheses) >= 2
    assert hypotheses[0]["id"] == "hyp_1"

    # Validate review listing
    review = res_data["review"]
    reviews = review.get("reviews", [])
    assert len(reviews) >= 2
    assert reviews[0]["hypothesis_id"] == "hyp_1"

    # Validate decision root cause details
    root_cause_data = res_data["root_cause"]
    root_cause = root_cause_data.get("root_cause", {})
    assert root_cause["confidence"] > 0.0
    assert "payments" in root_cause["description"].lower() or "connection" in root_cause["description"].lower()
    assert len(root_cause_data.get("alternatives", [])) >= 1
    assert "reasoning" in root_cause_data

    # 5. Verify database persistence via GET endpoints
    # Get Hypotheses
    get_hyp = client.get(f"/api/v1/workspaces/{workspace_id}/hypotheses")
    assert get_hyp.status_code == 200
    assert len(get_hyp.json().get("hypotheses", [])) == len(hypotheses)

    # Get Review
    get_rev = client.get(f"/api/v1/workspaces/{workspace_id}/review")
    assert get_rev.status_code == 200
    assert len(get_rev.json().get("reviews", [])) == len(reviews)

    # Get Root Cause
    get_rc = client.get(f"/api/v1/workspaces/{workspace_id}/root-cause")
    assert get_rc.status_code == 200
    assert get_rc.json().get("root_cause", {}).get("title") == root_cause["title"]

    logger.info("Stage 3 E2E Integration Pipeline Test Passed Successfully!")
