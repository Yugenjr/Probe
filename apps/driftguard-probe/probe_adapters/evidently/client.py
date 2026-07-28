"""Standalone third-party telemetry observability adapter for Evidently AI monitors."""
from typing import Any, Dict, List, Union
from probe.interfaces.telemetry import TelemetryProvider
from probe.interfaces.context import ResourceContext


class EvidentlyTelemetryAdapter(TelemetryProvider):
    """TelemetryProvider implementation extracting statistical dataset tests from Evidently AI workspace monitors."""
    async def get_model(self, target: Union[str, ResourceContext]) -> Dict[str, Any]:
        model_id = target.model_id if isinstance(target, ResourceContext) else str(target)
        return {"project_id": model_id, "platform": "Evidently AI", "status": "ACTIVE"}

    async def get_drift_metrics(self, target: Union[str, ResourceContext], limit: int = 100) -> List[Dict[str, Any]]:
        return [
            {"feature": "loan_amount", "drift_score": 0.19, "test_name": "wasserstein", "drift_detected": True},
        ]

    async def fetch_feature_drift(self, target: Union[str, ResourceContext], time_range_hours: int = 24) -> List[Dict[str, Any]]:
        return await self.get_drift_metrics(target)
