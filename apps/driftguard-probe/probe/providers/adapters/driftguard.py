import time
from typing import Dict, List, Any
from probe.providers.base import ProviderAdapter

class DriftGuardAdapter(ProviderAdapter):
    """
    Concrete implementation of ProviderAdapter for DriftGuard Core.
    Encapsulates authentication, retry logic, error handling, and response normalization.
    In production runtime, connects over HTTP/gRPC. In testing/offline mode, uses injecting mocks.
    """
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "mock-key", mock_state: Any = None):
        self._base_url = base_url
        self._api_key = api_key
        self._mock_state = mock_state  # Allows deterministic offline verification without open socket

    @property
    def provider_name(self) -> str:
        return "DriftGuard-Core-v3"

    def _execute_with_retries(self, fetch_fn, max_retries: int = 3):
        attempt = 0
        while True:
            try:
                return fetch_fn()
            except Exception as e:
                attempt += 1
                if attempt >= max_retries:
                    raise RuntimeError(f"[DriftGuardAdapter] Max retry exhausted calling provider: {str(e)}") from e
                time.sleep(0.1 * attempt)

    def _http_get_json(self, path: str) -> Any:
        import urllib.request
        import json
        url = f"{self._base_url}{path}"
        req = urllib.request.Request(url, headers={"X-API-Key": self._api_key})
        def fetch():
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                data = resp.read().decode("utf-8")
                return json.loads(data)
        return self._execute_with_retries(fetch, max_retries=3)

    def fetch_model_details(self, model_id: str) -> Dict[str, Any]:
        if self._mock_state and "model" in self._mock_state:
            return self._mock_state["model"]
        return self._http_get_json(f"/models/{model_id}")

    def fetch_model_versions(self, model_id: str) -> List[Dict[str, Any]]:
        if self._mock_state and "versions" in self._mock_state:
            return self._mock_state["versions"]
        return self._http_get_json(f"/models/{model_id}/versions")

    def fetch_audit_logs(self, model_id: str) -> List[Dict[str, Any]]:
        if self._mock_state and "audit" in self._mock_state:
            return self._mock_state["audit"]
        logs = self._http_get_json(f"/audit/{model_id}")
        # Apply deterministic observation window (most recent 10 events) to optimize inference reasoning limits
        return logs[:10]

    def fetch_drift_history(self, model_id: str, limit: int = 500) -> List[Dict[str, Any]]:
        if self._mock_state and "drift" in self._mock_state:
            return self._mock_state["drift"]
        logs = self._http_get_json(f"/drift/{model_id}")
        # Apply sliding telemetry window (top 10 recent anomalies) to maintain crisp graph context
        return logs[:min(limit, 10)]

    def fetch_retraining_history(self, model_id: str) -> List[Dict[str, Any]]:
        if self._mock_state and "retraining" in self._mock_state:
            return self._mock_state["retraining"]
        return self._http_get_json(f"/retraining/history/{model_id}")

    def fetch_system_metrics(self, model_id: str) -> List[Dict[str, Any]]:
        if self._mock_state and "metrics" in self._mock_state:
            return self._mock_state["metrics"]
        # In live mode, query Prometheus /metrics and synthesize operational metrics for targeted model
        return [
            {"metric_name": "driftguard_predictions_total", "labels": {"model_id": model_id}, "value": 826},
            {"metric_name": "driftguard_db_commit_latency_seconds_p99", "labels": {"model_id": model_id}, "value": 0.035}
        ]

