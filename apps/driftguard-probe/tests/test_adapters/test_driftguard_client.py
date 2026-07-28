"""Unit tests verifying DriftGuard REST client behavior and protocol adherence."""
import asyncio
import pytest
from probe.adapters.driftguard.client import DriftGuardRESTClient
from probe.adapters.driftguard.auth import DriftGuardAuth
from probe.interfaces.adapter import PlatformProvider


def test_driftguard_client_implements_protocol():
    """Verify DriftGuardRESTClient satisfies abstract PlatformProvider contract at runtime."""
    client = DriftGuardRESTClient()
    assert isinstance(client, PlatformProvider)


def test_auth_headers_generation():
    """Ensure API key token is securely attached to headers dictionary when provided."""
    auth = DriftGuardAuth(api_key="secret-dg-key-123")
    headers = auth.get_headers()
    assert headers.get("X-API-Key") == "secret-dg-key-123"
    assert headers.get("Content-Type") == "application/json"


def test_driftguard_client_methods(mock_adapter: PlatformProvider):
    """Verify platform provider mock interfaces respond with structured dictionaries."""
    async def _test_run():
        model_data = await mock_adapter.get_model("test-model")
        assert model_data["version"] == "9.9.9"

        retrain = await mock_adapter.trigger_retraining("test-model")
        assert retrain["status"] == "DISPATCHED"

    asyncio.run(_test_run())
