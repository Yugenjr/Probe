"""Standalone third-party telemetry observability adapter for Arize AI models."""
from typing import Any, Dict, List, Union
from probe.interfaces.telemetry import TelemetryProvider
from probe.interfaces.context import ResourceContext


class ArizeTelemetryAdapter(TelemetryProvider):
    """TelemetryProvider implementation extracting model monitor indices from Arize AI workspaces."""
    async def get_model(self, target: Union[str, ResourceContext]) -> Dict[str, Any]:
        model_id = target.model_id if isinstance(target, ResourceContext) else str(target)
        return {"model_id": model_id, "platform": "Arize AI", "model_type": "SCORE_CATEGORICAL"}

    async def get_drift_metrics(self, target: Union[str, ResourceContext], limit: int = 100) -> List[Dict[str, Any]]:
        return [
            {"dimension": "prediction_entropy", "drift_value": 0.25, "metric_type": "PSI", "alert_triggered": True},
        ]

    async def fetch_feature_drift(self, target: Union[str, ResourceContext], time_range_hours: int = 24) -> List[Dict[str, Any]]:
        return await self.get_drift_metrics(target)
