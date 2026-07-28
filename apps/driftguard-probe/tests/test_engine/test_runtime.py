"""Unit and integration tests verifying the complete agent runtime workflow lifecycle."""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from probe.engine.state import InvestigationSession, InvestigationStatus
from probe.engine.runtime import get_investigation_runtime
from probe.storage.session_repository import get_session_repository


@pytest.fixture
def clean_repository():
    """Ensure repository is empty before each test run."""
    repo = get_session_repository()
    repo._storage.clear()
    return repo


@pytest.mark.anyio
async def test_runtime_direct_execution(clean_repository):
    """Verify that start_investigation executes all agents in the plan and completes successfully."""
    from probe.domain.incident import Incident, IncidentSeverity
    
    incident = Incident(
        incident_id="inc-test-direct",
        model_id="demo-rollback-v2",
        trigger_type="drift_detected",
        severity=IncidentSeverity.MEDIUM,
        raw_payload={}
    )
    
    session = InvestigationSession(
        session_id="inv-test-direct",
        investigation_id="inv-test-direct",
        status=InvestigationStatus.CREATED,
        incident=incident
    )
    
    await clean_repository.save(session)
    
    runtime = get_investigation_runtime()
    
    # Run the investigation workflow
    await runtime.start_investigation(session.session_id)
    
    # Retrieve updated session
    updated_session = await clean_repository.get(session.session_id)
    
    assert updated_session is not None
    assert updated_session.status == InvestigationStatus.COMPLETED
    
    # Verify Supervisor logs
    assert any("Supervisor generated execution plan" in entry for entry in updated_session.execution_history)
    # Verify Planner logs
    assert any("[Planner] Generated InvestigationPlan" in entry for entry in updated_session.execution_history)
    # Verify Investigator evidence was added
    assert len(updated_session.universal_evidence) == 1
    assert updated_session.universal_evidence[0].evidence_type == "drift_stats"
    # Verify Reporter compiled report
    assert updated_session.report is not None
    assert "Incident Investigation Report" in updated_session.report.markdown_content


@patch("probe.services.investigation_service.DriftGuardClient")
def test_webhook_triggers_async_runtime(mock_client_class, api_client: TestClient, clean_repository):
    """Verify that posting to webhooks triggers the runtime in the background and completes the session."""
    mock_client = mock_client_class.return_value
    mock_client.aget_model_details = AsyncMock(return_value={
        "model_id": "demo-rollback-v2",
        "status": "degraded",
        "version": "1.0.0",
        "drift_threshold": 0.15,
        "features": [],
        "reference_data_path": ""
    })
    mock_client.aget_model_versions = AsyncMock(return_value=[])
    mock_client.aget_drift_history = AsyncMock(return_value=[])
    mock_client.aget_audit_logs = AsyncMock(return_value=[])
    mock_client.aget_retraining_history = AsyncMock(return_value=[])
    mock_client.aget_metrics = AsyncMock(return_value="")
    mock_client.aclose = AsyncMock()

    payload = {
        "model_id": "demo-rollback-v2"
    }

    # Trigger webhook POST
    resp = api_client.post("/api/v1/webhooks", json=payload)
    assert resp.status_code == 202
    session_id = resp.json()["investigation_id"]

    # Sleep briefly to allow the async EventBus task to run the investigation pipeline
    import time
    start = time.time()
    completed = False
    
    # Poll repository up to 2 seconds for status = COMPLETED
    repo = get_session_repository()
    while time.time() - start < 2.0:
        session = repo._storage.get(session_id)
        if session and session.status == InvestigationStatus.COMPLETED:
            completed = True
            break
        time.sleep(0.05)

    assert completed is True
    session = repo._storage.get(session_id)
    assert session is not None
    assert session.status == InvestigationStatus.COMPLETED
    assert session.report is not None
