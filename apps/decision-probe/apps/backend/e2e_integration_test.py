import time
import json
import logging
import io
import os
from fastapi.testclient import TestClient

# Mock the database engine to use a local test database
os.environ["TEST_DB"] = "1"
import storage.database
from sqlmodel import create_engine, SQLModel, Session

test_engine = create_engine("sqlite:///e2e_test.db", connect_args={"check_same_thread": False})
storage.database.engine = test_engine

from main import app
from storage.database import get_session
from storage.models import Workspace, Block, Document, DocumentChunk

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Ensure tables are created on the test engine
SQLModel.metadata.drop_all(test_engine)
SQLModel.metadata.create_all(test_engine)

client = TestClient(app)

def run_e2e_pipeline():
    logger.info("==================================================")
    logger.info("Starting Stage 1 E2E Integration Pipeline Test")
    logger.info("==================================================")

    # 1. Create Workspace
    logger.info("Step 1: POST /api/v1/workspaces")
    response = client.post("/api/v1/workspaces", json={"title": "E2E Investigation Workspace", "initial_blocks": []})
    assert response.status_code == 200
    ws_data = response.json()
    workspace_id = ws_data["id"]
    logger.info(f"✓ Workspace created with ID: {workspace_id}")

    # 2. Upload file to trigger parse/chunk/embed background pipeline
    logger.info(f"Step 2: POST /api/v1/workspaces/{workspace_id}/upload")
    file_content = "ERROR: connection timed out after 30 seconds to billing database.\n" * 5
    file_data = {"file": ("billing_logs.log", io.BytesIO(file_content.encode("utf-8")), "text/plain")}
    
    upload_response = client.post(f"/api/v1/workspaces/{workspace_id}/upload", files=file_data)
    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    doc_id = upload_data["id"]
    logger.info(f"✓ File uploaded successfully, doc_id: {doc_id}")

    # 3. Poll status until all_indexed is true (background task finishes)
    logger.info(f"Step 3: GET /api/v1/workspaces/{workspace_id}/status (polling progress)")
    indexed = False
    for attempt in range(10):
        status_response = client.get(f"/api/v1/workspaces/{workspace_id}/status")
        assert status_response.status_code == 200
        status_data = status_response.json()
        logger.info(f"Poll {attempt+1}: all_indexed={status_data['all_indexed']}")
        if status_data["all_indexed"]:
            indexed = True
            break
        time.sleep(0.5)
    
    assert indexed, "Document processing timed out in background tasks!"
    logger.info("✓ Background parsing, chunking, and embedding indexing complete")

    # 4. Start Investigation to invoke Retrieval and Planner Agent
    logger.info(f"Step 4: POST /api/v1/workspaces/{workspace_id}/investigate")
    investigate_goal = "Analyze the billing logs for errors and timeouts"
    investigate_response = client.post(
        f"/api/v1/workspaces/{workspace_id}/investigate",
        json={"goal": investigate_goal}
    )
    assert investigate_response.status_code == 200
    res_dict = investigate_response.json()
    assert "plan" in res_dict
    plan_data = res_dict["plan"]
    assert "objectives" in plan_data
    assert "priority" in plan_data
    logger.info(f"✓ Planner Agent generated plan: {json.dumps(plan_data)}")

    # 5. Retrieve Plan via GET endpoint
    logger.info(f"Step 5: GET /api/v1/workspaces/{workspace_id}/plan")
    plan_response = client.get(f"/api/v1/workspaces/{workspace_id}/plan")
    assert plan_response.status_code == 200
    retrieved_plan = plan_response.json()
    assert retrieved_plan["priority"] == plan_data["priority"]
    logger.info("✓ Retrieved plan details correctly")

    # 6. Verify plan is stored as a Block in Workspace
    logger.info(f"Step 6: GET /api/v1/workspaces/{workspace_id} (Verifying Blocks)")
    ws_response = client.get(f"/api/v1/workspaces/{workspace_id}")
    assert ws_response.status_code == 200
    ws_blocks_data = ws_response.json()
    blocks = ws_blocks_data.get("blocks", [])
    
    # We should have a block of type "plan"
    plan_blocks = [b for b in blocks if b["type"] == "plan"]
    assert len(plan_blocks) == 1, "Expected exactly one plan block in the workspace"
    assert plan_blocks[0]["content"]["priority"] == plan_data["priority"]
    
    logger.info("✓ Block storage verified (block of type 'plan' is stored)")

    print("\n" + "="*50)
    print("STAGE 1 END-TO-END INTEGRATION TEST PASSED!")
    print(f"Workspace ID: {workspace_id}")
    print(f"Document ID: {doc_id}")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_e2e_pipeline()
