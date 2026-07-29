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


@pytest.fixture(autouse=True)
def mock_driftguard_client_global():
    """Globally mock DriftGuardClient to prevent tests from hitting live port 8000."""
    from unittest.mock import MagicMock, AsyncMock, patch
    with patch("probe.services.investigation_service.DriftGuardClient") as mock_service_client, \
         patch("probe.providers.adapters.driftguard.DriftGuardClient") as mock_adapter_client, \
         patch("probe.services.driftguard_client.DriftGuardClient") as mock_client_client:
        
        # Configure all mock classes to use the same mock instance
        for mock_class in (mock_service_client, mock_adapter_client, mock_client_client):
            mock_instance = mock_class.return_value
            
            # Async methods mocking
            mock_instance.aget_model_details = AsyncMock(return_value={
                "model_id": "test-model",
                "status": "active",
                "version": "9.9.9",
                "drift_threshold": 0.15,
                "features": [],
                "reference_data_path": "",
                "created_at": "2026-07-28T12:00:00"
            })
            mock_instance.aget_model_versions = AsyncMock(return_value=[
                {"version": "9.9.9", "status": "champion"}
            ])
            mock_instance.aget_drift_history = AsyncMock(return_value=[
                {"timestamp": "2026-07-28T12:00:00Z", "drift_score": 0.25, "features": {}, "prediction": {}}
            ])
            mock_instance.aget_audit_logs = AsyncMock(return_value=[])
            mock_instance.aget_retraining_history = AsyncMock(return_value=[])
            mock_instance.aget_metrics = AsyncMock(return_value="")
            mock_instance.atrigger_retraining = AsyncMock(return_value={"status": "DISPATCHED"})
            
            # Sync methods mocking
            mock_instance.get_model_details = MagicMock(return_value={
                "model_id": "test-model",
                "status": "active",
                "version": "9.9.9",
                "drift_threshold": 0.15,
                "features": [],
                "reference_data_path": "",
                "created_at": "2026-07-28T12:00:00"
            })
            mock_instance.get_model_versions = MagicMock(return_value=[])
            mock_instance.get_drift_history = MagicMock(return_value=[])
            mock_instance.get_audit_logs = MagicMock(return_value=[])
            mock_instance.get_retraining_history = MagicMock(return_value=[])
            mock_instance.get_metrics = MagicMock(return_value="")
            mock_instance.trigger_retraining = MagicMock(return_value={"status": "DISPATCHED"})
            
            mock_instance.aclose = AsyncMock()
            mock_instance.close = MagicMock()
            
        yield mock_service_client.return_value


@pytest.fixture(autouse=True)
def mock_mcp_infrastructure():
    """Ensure every test runs with an isolated, clean local-only MCP infrastructure."""
    from probe.core.di import get_container
    from probe.mcp.registry.server_registry import ServerRegistry
    from probe.mcp.gateway.tool_gateway import ToolGateway
    from probe.evidence.evidence_gateway import EvidenceGateway
    from probe.mcp.servers.knowledge.server import KnowledgeServer

    container = get_container()
    
    # Save original providers
    orig_registry = getattr(container, "mcp_registry", None)
    orig_gateway = getattr(container, "tool_gateway", None)
    orig_evidence = getattr(container, "evidence_gateway", None)

    # Setup isolated local-only instance
    registry = ServerRegistry()
    registry.register(KnowledgeServer())
    
    gateway = ToolGateway(registry=registry)
    evidence = EvidenceGateway(tool_gateway=gateway)

    container.mcp_registry = registry
    container.tool_gateway = gateway
    container.evidence_gateway = evidence

    yield

    # Restore originals (if any)
    container.mcp_registry = orig_registry
    container.tool_gateway = orig_gateway
    container.evidence_gateway = orig_evidence


@pytest.fixture(autouse=True)
async def clean_database():
    """Clean all tables in PostgreSQL before running a test."""
    from probe.database.connection import async_session_factory
    from sqlalchemy import text
    async with async_session_factory() as session:
        try:
            # Disable triggers and truncate all tables to clean state
            await session.execute(text("TRUNCATE TABLE investigations CASCADE"))
            await session.execute(text("TRUNCATE TABLE mcp_servers CASCADE"))
            await session.execute(text("TRUNCATE TABLE audit_logs CASCADE"))
            await session.commit()
        except Exception:
            await session.rollback()


