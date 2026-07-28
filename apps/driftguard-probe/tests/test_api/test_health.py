"""Unit tests verifying FastAPI gateway HTTP endpoints."""
from fastapi.testclient import TestClient


def test_health_endpoint(api_client: TestClient):
    """Verify /api/v1/health responds with successful operational metrics."""
    response = api_client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["data"]["status"] == "HEALTHY"


def test_webhook_acceptance(api_client: TestClient):
    """Verify incoming anomaly event payload returns 202 Accepted status and investigation ID."""
    dummy_event = {
        "source_platform": "driftguard",
        "event_type": "drift_detected",
        "model_id": "test_churn_model",
        "model_version": "1.0.1",
        "details": {"score": 0.22},
    }
    response = api_client.post("/api/v1/webhooks", json=dummy_event)
    assert response.status_code == 202
    payload = response.json()
    assert payload["status"] == "ACCEPTED"
    assert "inv-" in payload["investigation_id"]
