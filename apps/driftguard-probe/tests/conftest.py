"""Pytest configuration fixtures and test-double mocks."""
import pytest
from typing import Any, Dict, List, Optional
from fastapi.testclient import TestClient
from probe.api.main import create_app
from probe.interfaces.adapter import PlatformProvider
from probe.core.config import Settings


class MockPlatformAdapter(PlatformProvider):
    """Mock platform implementation insulating unit test runs from actual external network IO."""
    async def get_model(self, model_id: str) -> Dict[str, Any]:
        return {"model_id": model_id, "status": "active", "version": "9.9.9"}

    async def get_drift_metrics(self, model_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        return [{"metric": "test_drift", "value": 0.25}]

    async def get_validation_records(self, model_id: str) -> List[Dict[str, Any]]:
        return [{"check": "test_null_check", "status": "PASSED"}]

    async def get_audit_logs(self, model_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        return [{"log_id": 100, "event_type": "drift_alert", "details": "Simulated audit message"}]

    async def get_reports(self, model_id: str) -> List[Dict[str, Any]]:
        return [{"report_id": "rep-test-01", "title": "Test Health Review"}]

    async def trigger_retraining(self, model_id: str, dataset_path: Optional[str] = None) -> Dict[str, Any]:
        return {"status": "DISPATCHED", "test_mock": True}


@pytest.fixture
def mock_adapter() -> PlatformProvider:
    """Provide clean instance of MockPlatformAdapter."""
    return MockPlatformAdapter()


@pytest.fixture
def test_settings() -> Settings:
    """Yield isolated test environmental settings."""
    return Settings(
        driftguard_base_url="http://mock.server:8000",
        llm_provider="base",
        enable_telemetry=False,
        debug_mode=True,
    )


@pytest.fixture
def api_client() -> TestClient:
    """Yield synchronous test client for FastAPI gateway endpoints."""
    app = create_app()
    with TestClient(app) as client:
        yield client
