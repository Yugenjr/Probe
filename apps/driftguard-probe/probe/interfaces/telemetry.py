"""Telemetry monitoring interface protocol definition."""
from typing import Any, Dict, List, Optional, Protocol, Union, runtime_checkable
from .context import ResourceContext


@runtime_checkable
class TelemetryProvider(Protocol):
    """Protocol defining read-only observability, quantitative metrics, and statistical drift extraction.
    
    Implemented by monitoring platforms such as DriftGuard, WhyLabs, Evidently AI, and Arize AI.
    """
    async def get_model(self, target: Union[str, ResourceContext]) -> Dict[str, Any]:
        """Retrieve deployment architecture version lineage and status metadata."""
        ...

    async def get_drift_metrics(self, target: Union[str, ResourceContext], limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve statistical feature drift calculations and calculated anomaly scores."""
        ...

    async def fetch_feature_drift(self, target: Union[str, ResourceContext], time_range_hours: int = 24) -> List[Dict[str, Any]]:
        """Fetch statistical distribution drift across all monitored feature dimensions."""
        ...
