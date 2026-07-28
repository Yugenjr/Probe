import logging
import time
from typing import Dict, List, Any, Optional
from probe.providers.base import ProviderAdapter
from probe.services.driftguard_client import DriftGuardClient

logger = logging.getLogger(__name__)


class DriftGuardAdapter(ProviderAdapter):
    """
    Concrete implementation of ProviderAdapter for DriftGuard Core.
    Delegates all HTTP/REST calls to the reusable DriftGuardClient.
    """
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, mock_state: Any = None):
        from probe.core.config import get_settings
        settings = get_settings()
        self._base_url = (base_url or settings.driftguard_base_url).rstrip("/")
        self._api_key = api_key or settings.driftguard_api_key
        self._mock_state = mock_state  # Allows deterministic offline verification without open socket
        self._client = DriftGuardClient(base_url=self._base_url, api_key=self._api_key)

    @property
    def provider_name(self) -> str:
        return "DriftGuard-Core-v3"

    def fetch_model_details(self, model_id: str) -> Dict[str, Any]:
        if self._mock_state and "model" in self._mock_state:
            return self._mock_state["model"]
        return self._client.get_model_details(model_id)

    def fetch_model_versions(self, model_id: str) -> List[Dict[str, Any]]:
        if self._mock_state and "versions" in self._mock_state:
            return self._mock_state["versions"]
        return self._client.get_model_versions(model_id)

    def fetch_audit_logs(self, model_id: str) -> List[Dict[str, Any]]:
        if self._mock_state and "audit" in self._mock_state:
            return self._mock_state["audit"]
        logs = self._client.get_audit_logs(model_id)
        # Apply deterministic observation window (most recent 10 events) to optimize inference reasoning limits
        return logs[:10]

    def fetch_drift_history(self, model_id: str, limit: int = 500) -> List[Dict[str, Any]]:
        if self._mock_state and "drift" in self._mock_state:
            return self._mock_state["drift"]
        logs = self._client.get_drift_history(model_id)
        # Apply sliding telemetry window (top 10 recent anomalies) to maintain crisp graph context
        return logs[:min(limit, 10)]

    def fetch_retraining_history(self, model_id: str) -> List[Dict[str, Any]]:
        if self._mock_state and "retraining" in self._mock_state:
            return self._mock_state["retraining"]
        return self._client.get_retraining_history(model_id)

    def fetch_system_metrics(self, model_id: str) -> List[Dict[str, Any]]:
        if self._mock_state and "metrics" in self._mock_state:
            return self._mock_state["metrics"]
        try:
            raw_metrics = self._client.get_metrics()
            from probe.services.investigation_service import parse_prometheus_metrics
            return parse_prometheus_metrics(raw_metrics, model_id)
        except Exception as e:
            logger.warning("Failed to fetch/parse Prometheus metrics in DriftGuardAdapter: %s", e)
            from probe.services.investigation_service import parse_prometheus_metrics
            return parse_prometheus_metrics("", model_id)

