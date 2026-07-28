"""Unit tests verifying webhook endpoint routing, authentication handling, and context assembly."""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import status

from probe.services.driftguard_client import (
    DriftGuardAuthenticationError,
    DriftGuardNotFoundError,
    DriftGuardServerError,
    DriftGuardConnectionError,
)
from probe.storage.session_repository import get_session_repository


@pytest.fixture
def clean_repository():
    """Ensure repository is empty before each test run."""
    repo = get_session_repository()
    repo._storage.clear()
    return repo


@patch("probe.services.investigation_service.DriftGuardClient")
def test_receive_webhook_success(mock_client_class, api_client: TestClient, clean_repository):
    """Verify that posting a valid webhook creates a session and returns 202 Accepted."""
    # Setup mock client instance and async methods
    mock_client = mock_client_class.return_value
    mock_client.aget_model_details = AsyncMock(return_value={
        "model_id": "demo-rollback-fixed",
        "status": "degraded",
        "version": "1.0.0",
        "drift_threshold": 0.15,
        "features": ["feat1"],
        "reference_data_path": "s3://ref",
        "created_at": "2026-07-28T12:00:00"
    })
    mock_client.aget_model_versions = AsyncMock(return_value=[
        {"version": "1.0.0", "status": "champion", "accuracy": 0.95}
    ])
    mock_client.aget_drift_history = AsyncMock(return_value=[
        {
            "timestamp": "2026-07-28T12:00:00Z",
            "drift_score": 0.25,
            "features": {"feat1": 0.5},
            "prediction": {"output": 1.0}
        }
    ])
    mock_client.aget_audit_logs = AsyncMock(return_value=[
        {
            "event_type": "drift_detected",
            "timestamp": "2026-07-28T12:00:00Z",
            "details": {"message": "Drift score exceeded threshold"}
        }
    ])
    mock_client.aget_retraining_history = AsyncMock(return_value=[])
    mock_client.aget_metrics = AsyncMock(return_value="driftguard_predictions_total{model_id=\"demo-rollback-fixed\"} 826.0")
    mock_client.aclose = AsyncMock()

    payload = {
        "event_id": 123,
        "model_id": "demo-rollback-fixed",
        "drift_score": 0.25,
        "callback_url": "http://localhost:8000/retrain/demo-rollback-fixed/complete"
    }

    resp = api_client.post("/api/v1/webhooks", json=payload)
    assert resp.status_code == status.HTTP_202_ACCEPTED
    data = resp.json()
    assert data["status"] == "ACCEPTED"
    assert "investigation_id" in data

    # Verify session is persisted in the repository
    session_id = data["investigation_id"]
    session = clean_repository._storage.get(session_id)
    assert session is not None
    assert session.incident.model_id == "demo-rollback-fixed"
    assert session.investigation_context is not None
    assert session.investigation_context.model_version == "1.0.0"
    assert len(session.investigation_context.predictions) == 1


@patch("probe.services.investigation_service.DriftGuardClient")
def test_receive_webhook_unauthorized(mock_client_class, api_client: TestClient, clean_repository):
    """Verify that a 401/403 returned by SDK translates to a clean 401 unauthorized response."""
    mock_client = mock_client_class.return_value
    mock_client.aget_model_details = AsyncMock(side_effect=DriftGuardAuthenticationError(401, "Unauthorized token"))
    mock_client.aclose = AsyncMock()

    payload = {
        "model_id": "demo-rollback-fixed"
    }

    resp = api_client.post("/api/v1/webhooks", json=payload)
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in resp.json()
    assert "Unauthorized" in resp.json()["detail"]
    assert "stack_trace" not in resp.text


@patch("probe.services.investigation_service.DriftGuardClient")
def test_receive_webhook_not_found(mock_client_class, api_client: TestClient, clean_repository):
    """Verify that a 404 returned by SDK translates to a clean 404 response."""
    mock_client = mock_client_class.return_value
    mock_client.aget_model_details = AsyncMock(side_effect=DriftGuardNotFoundError(404, "Model not registered"))
    mock_client.aclose = AsyncMock()

    payload = {
        "model_id": "demo-rollback-fixed"
    }

    resp = api_client.post("/api/v1/webhooks", json=payload)
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    assert "detail" in resp.json()
    assert "Not Found" in resp.json()["detail"]


@patch("probe.services.investigation_service.DriftGuardClient")
def test_receive_webhook_server_error(mock_client_class, api_client: TestClient, clean_repository):
    """Verify that a 500 returned by SDK translates to a clean 500 response."""
    mock_client = mock_client_class.return_value
    mock_client.aget_model_details = AsyncMock(side_effect=DriftGuardServerError(500, "Database failure"))
    mock_client.aclose = AsyncMock()

    payload = {
        "model_id": "demo-rollback-fixed"
    }

    resp = api_client.post("/api/v1/webhooks", json=payload)
    assert resp.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "detail" in resp.json()
    assert "Internal Server Error" in resp.json()["detail"]


@patch("probe.services.investigation_service.DriftGuardClient")
def test_receive_webhook_connection_error(mock_client_class, api_client: TestClient, clean_repository):
    """Verify that a network failure translates to a clean 503 service unavailable response."""
    mock_client = mock_client_class.return_value
    mock_client.aget_model_details = AsyncMock(side_effect=DriftGuardConnectionError("Connection timed out"))
    mock_client.aclose = AsyncMock()

    payload = {
        "model_id": "demo-rollback-fixed"
    }

    resp = api_client.post("/api/v1/webhooks", json=payload)
    assert resp.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "detail" in resp.json()
    assert "Service Unavailable" in resp.json()["detail"]
