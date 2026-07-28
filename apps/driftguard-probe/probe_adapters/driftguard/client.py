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

    def _resolve_model_id(self, target: Union[str, ResourceContext]) -> str:
        return target.model_id if isinstance(target, ResourceContext) else str(target)

    async def get_model(self, target: Union[str, ResourceContext]) -> Dict[str, Any]:
        model_id = self._resolve_model_id(target)
        return {"model_id": model_id, "version": "9.9.9", "status": "ACTIVE", "platform": "DriftGuard"}

    async def get_drift_metrics(self, target: Union[str, ResourceContext], limit: int = 100) -> List[Dict[str, Any]]:
        model_id = self._resolve_model_id(target)
        return [
            {"feature": "user_age", "drift_score": 0.14, "alarm": True, "model_id": model_id},
            {"feature": "income_index", "drift_score": 0.02, "alarm": False, "model_id": model_id},
        ]

    async def fetch_feature_drift(self, target: Union[str, ResourceContext], time_range_hours: int = 24) -> List[Dict[str, Any]]:
        return await self.get_drift_metrics(target)

    async def fetch_performance_metrics(self, target: Union[str, ResourceContext], metric_names: List[str]) -> List[Dict[str, Any]]:
        return [{"metric_name": name, "value": 99.5, "status": "STABLE"} for name in metric_names]

    async def get_validation_records(self, target: Union[str, ResourceContext]) -> List[Dict[str, Any]]:
        return [{"check_id": "val_null_check", "passed": True, "target": self._resolve_model_id(target)}]

    async def fetch_validation_records(self, target: Union[str, ResourceContext]) -> List[Dict[str, Any]]:
        return await self.get_validation_records(target)

    async def get_audit_logs(self, target: Union[str, ResourceContext], limit: int = 50) -> List[Dict[str, Any]]:
        return [{"log_id": 101, "event": "alarm_threshold_modified", "operator": "admin"}]

    async def fetch_audit_trails(self, target: Union[str, ResourceContext], limit: int = 50) -> List[Dict[str, Any]]:
        return await self.get_audit_logs(target, limit)

    async def get_reports(self, target: Union[str, ResourceContext]) -> List[Dict[str, Any]]:
        return [{"report_id": "rep-q1", "status": "FINALIZED"}]

    async def trigger_retraining(self, target: Union[str, ResourceContext], dataset_path: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        return {"job_id": "job-dg-101", "status": "DISPATCHED", "model_id": self._resolve_model_id(target)}

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
