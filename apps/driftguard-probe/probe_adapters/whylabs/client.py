"""Standalone third-party telemetry observability adapter for WhyLabs profiles."""
from typing import Any, Dict, List, Union
from probe.interfaces.telemetry import TelemetryProvider
from probe.interfaces.context import ResourceContext
import httpx


class WhyLabsTelemetryAdapter(TelemetryProvider):
    """TelemetryProvider implementation connecting WhyLabs statistical observability profiles to Probe."""
    def __init__(self, api_key: str = "demo-whylabs-key", org_id: str = "org-demo"):
        self.api_key = api_key
        self.org_id = org_id
        self._client = httpx.AsyncClient(base_url="https://api.whylabs.ai/v0", timeout=10.0)

    async def get_model(self, target: Union[str, ResourceContext]) -> Dict[str, Any]:
        dataset_id = target.model_id if isinstance(target, ResourceContext) else str(target)
        return {"dataset_id": dataset_id, "platform": "WhyLabs", "status": "ACTIVE", "org_id": self.org_id}

    async def get_drift_metrics(self, target: Union[str, ResourceContext], limit: int = 100) -> List[Dict[str, Any]]:
        dataset_id = target.model_id if isinstance(target, ResourceContext) else str(target)
        return [
            {"feature_name": "annual_income", "drift_score": 0.22, "algorithm": "kl_divergence", "dataset_id": dataset_id},
            {"feature_name": "credit_score", "drift_score": 0.04, "algorithm": "kl_divergence", "dataset_id": dataset_id},
        ]

    async def fetch_feature_drift(self, target: Union[str, ResourceContext], time_range_hours: int = 24) -> List[Dict[str, Any]]:
        return await self.get_drift_metrics(target)
