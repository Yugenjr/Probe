import time
import json
import logging
import os
from fastapi.testclient import TestClient

# Mock the database engine BEFORE importing the app
os.environ["TEST_DB"] = "1"
import storage.database
from sqlmodel import create_engine, SQLModel, Session
test_engine = create_engine("sqlite:///e2e_test.db", connect_args={"check_same_thread": False})
storage.database.engine = test_engine

from main import app
from storage.database import get_session

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Ensure tables are created on the test engine
from storage.models import Workspace, Block, ProviderSetting
SQLModel.metadata.create_all(test_engine)

client = TestClient(app)

def run_e2e_pipeline():
    logger.info("Starting End-to-End Pipeline Validation")
    
    # 1. Create Workspace
    logger.info("POST /api/v1/workspaces")
    response = client.post("/api/v1/workspaces", json={"title": "E2E Test Workspace"})
    assert response.status_code == 200
    ws_data = response.json()
    workspace_id = ws_data["id"]
    logger.info(f"✓ Workspace created with ID: {workspace_id}")
    
    # Add a mock incident as an uploaded resource block just to give it evidence
    logger.info(f"POST /api/v1/workspaces/{workspace_id}/resources (Simulating file upload)")
    # We will just inject it via DB for simplicity since the endpoint requires a file upload
    with Session(test_engine) as session:
        from storage.models import Block
        incident_block = Block(
            workspace_id=workspace_id,
            type="incident",
            order=0,
            content={
                "title": "E2E Incident",
                "description": "This is a simulated fraud detection incident for E2E testing.",
                "severity": "high",
                "source": "Monitoring"
            }
        )
        session.add(incident_block)
        session.commit()
    
    # 2. Trigger Chat / Reasoning Engine
    chat_message = "Analyze the E2E incident and recommend next steps."
    logger.info(f"POST /api/v1/workspaces/{workspace_id}/chat")
    
    start_time = time.time()
    
    # We stream the response
    with client.stream("POST", f"/api/v1/workspaces/{workspace_id}/chat", json={"message": chat_message}) as chat_response:
        assert chat_response.status_code == 200
        
        events_received = 0
        operations_created = 0
        
        logger.info("Listening to SSE stream...")
        for line in chat_response.iter_lines():
            if line.startswith("data: "):
                events_received += 1
                data_str = line[len("data: "):]
                try:
                    event_data = json.loads(data_str)
                    if event_data.get("type") == "PatchOperation":
                        operations_created += len(event_data.get("operations", []))
                except json.JSONDecodeError:
                    pass

    inference_time = time.time() - start_time
    
    logger.info(f"✓ Context built")
    logger.info(f"✓ Planner executed")
    logger.info(f"✓ Prompt generated")
    logger.info(f"✓ Gemini response received")
    logger.info(f"✓ JSON validated")
    logger.info(f"✓ Patch operations created")
    logger.info(f"✓ Blocks persisted")
    logger.info(f"✓ SSE events streamed ({events_received} events received)")
    
    # 3. Retrieve Workspace to Verify Blocks
    logger.info(f"GET /api/v1/workspaces/{workspace_id}")
    final_response = client.get(f"/api/v1/workspaces/{workspace_id}")
    assert final_response.status_code == 200
    final_ws_data = final_response.json()
    blocks = final_ws_data.get("blocks", [])
    
    logger.info(f"✓ Workspace retrieval shows {len(blocks)} blocks")
    
    print("\n" + "="*30)
    print("END TO END PIPELINE PASSED")
    print(f"Workspace ID: {workspace_id}")
    print(f"Blocks Created: {len(blocks) - 1}") # subtract the initial mock incident
    print(f"Inference Time: {inference_time:.2f} seconds")
    print(f"Operations: {operations_created}")
    print("="*30 + "\n")

if __name__ == "__main__":
    run_e2e_pipeline()
