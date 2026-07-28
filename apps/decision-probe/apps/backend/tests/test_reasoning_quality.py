import pytest
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from services.models import ReasoningContext, ResourceBundle
from inference.client import InferenceClient

TESTS_DIR = Path(__file__).parent

def load_incident(filename: str):
    filepath = TESTS_DIR / filename
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

@pytest.fixture
def client():
    # Only run if we have a real API key, otherwise skip
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key or groq_key == "dummy_key_for_testing" or groq_key == "dummy":
        pytest.skip("GROQ_API_KEY not set or is dummy")
    return InferenceClient()

def create_context(incident: dict) -> ReasoningContext:
    return ReasoningContext(
        workspace_id="test_ws",
        workspace_title=incident["title"],
        user_prompt=f"Investigate the incident: {incident['title']}",
        timestamp=datetime.now(timezone.utc),
        resources=ResourceBundle(evidence=[incident])
    )

@pytest.mark.asyncio
@pytest.mark.parametrize("incident_file", [
    "fraud_detection.json",
    "feature_drift.json",
    "latency_spike.json",
    "customer_churn.json",
    "payment_failure.json"
])
async def test_reasoning_quality(client, incident_file):
    incident = load_incident(incident_file)
    context = create_context(incident)
    
    response = await client.generate(context)
    
    assert response is not None
    assert len(response.operations) > 0
    
    types_found = [op.payload.type for op in response.operations if op.payload]
    
    # Check that we have a reasoning or decision block
    assert "reasoning" in types_found or "decision" in types_found or "investigation" in types_found or "incident" in types_found
    
    # If a decision was generated, verify decision quality rules
    for op in response.operations:
        if op.payload and op.payload.type == "decision":
            content = op.payload.content
            # Check decision structure
            assert "Decision" in content or "decision" in content or "Recommended Next Step" in content
            
            # Should have some reference to evidence since it was provided
            assert len(content.keys()) > 3 # ensures it's detailed
