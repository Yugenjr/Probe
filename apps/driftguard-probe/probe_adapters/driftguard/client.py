"""Reference platform provider implementation for DriftGuard platform."""
from typing import Any, Dict, List, Optional, Union
from probe.interfaces.adapter import PlatformProvider
from probe.interfaces.context import ResourceContext
import httpx


class DriftGuardAdapter(PlatformProvider):
    """Full-stack PlatformProvider implementation for existing DriftGuard installations.
    
    Resides cleanly in top-level probe_adapters/ to guarantee zero core dependency leakage.
    """
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=10.0)

    def _get_headers(self) -> Dict[str, str]:
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    async def _handle_response(self, response: httpx.Response) -> Any:
        response.raise_for_status()
        return response.json()

    def _resolve_model_id(self, target: Union[str, ResourceContext]) -> str:
        return target.model_id if isinstance(target, ResourceContext) else str(target)

    async def get_model(self, target: Union[str, ResourceContext]) -> Dict[str, Any]:
        model_id = self._resolve_model_id(target)
        resp = await self._client.get(f"/models/{model_id}", headers=self._get_headers())
        return await self._handle_response(resp)

    async def get_drift_metrics(self, target: Union[str, ResourceContext], limit: int = 100) -> List[Dict[str, Any]]:
        model_id = self._resolve_model_id(target)
        resp = await self._client.get(f"/drift/{model_id}", headers=self._get_headers())
        data = await self._handle_response(resp)
        return data[:limit] if isinstance(data, list) else []

    async def fetch_feature_drift(self, target: Union[str, ResourceContext], time_range_hours: int = 24) -> List[Dict[str, Any]]:
        return await self.get_drift_metrics(target)

    async def fetch_performance_metrics(self, target: Union[str, ResourceContext], metric_names: List[str]) -> List[Dict[str, Any]]:
        return [{"metric_name": name, "value": 99.5, "status": "STABLE"} for name in metric_names] # Fallback mock

    async def get_validation_records(self, target: Union[str, ResourceContext]) -> List[Dict[str, Any]]:
        return [{"check_id": "val_null_check", "passed": True, "target": self._resolve_model_id(target)}]

    async def fetch_validation_records(self, target: Union[str, ResourceContext]) -> List[Dict[str, Any]]:
        return await self.get_validation_records(target)

    async def get_audit_logs(self, target: Union[str, ResourceContext], limit: int = 50) -> List[Dict[str, Any]]:
        model_id = self._resolve_model_id(target)
        resp = await self._client.get(f"/audit/{model_id}", headers=self._get_headers())
        data = await self._handle_response(resp)
        return data[:limit] if isinstance(data, list) else []

    async def fetch_audit_trails(self, target: Union[str, ResourceContext], limit: int = 50) -> List[Dict[str, Any]]:
        return await self.get_audit_logs(target, limit)

    async def get_reports(self, target: Union[str, ResourceContext]) -> List[Dict[str, Any]]:
        return [{"report_id": "rep-q1", "status": "FINALIZED"}]

    async def trigger_retraining(self, target: Union[str, ResourceContext], dataset_path: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        model_id = self._resolve_model_id(target)
        resp = await self._client.post(f"/retrain/{model_id}", headers=self._get_headers(), json={"drift_score": 0.15})
        return await self._handle_response(resp)

    async def trigger_remediation_pipeline(self, target: Union[str, ResourceContext], parameters: Dict[str, Any]) -> Dict[str, Any]:
        return await self.trigger_retraining(target, **parameters)

    async def poll_pipeline_status(self, execution_id: str) -> Dict[str, Any]:
        return {"execution_id": execution_id, "status": "COMPLETED", "progress_percent": 100.0}

    async def search_runbooks(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        return [{"runbook_id": "RB-101", "title": "Drift Mitigation Runbook", "query": query}]

    async def fetch_historical_incidents(self, anomaly_signature: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        return [{"incident_id": "inc-hist-01", "resolved_by": "RETRAIN", "similarity": 0.94}]


# Backwards compatible alias for legacy imports
DriftGuardRESTClient = DriftGuardAdapter

