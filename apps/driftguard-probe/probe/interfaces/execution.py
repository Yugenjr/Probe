"""Execution and retraining pipeline interface protocol definition."""
from typing import Any, Dict, Optional, Protocol, Union, runtime_checkable
from .context import ResourceContext


@runtime_checkable
class ExecutionProvider(Protocol):
    """Protocol defining active automated model retraining and CI/CD remediation triggers.
    
    De-coupled from passive monitoring to ensure observability tools remain zero-modification compliant.
    """
    async def trigger_retraining(
        self, target: Union[str, ResourceContext], dataset_path: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Dispatch automated retraining pipeline job on validated dataset slices."""
        ...

    async def poll_pipeline_status(self, execution_id: str) -> Dict[str, Any]:
        """Verify asynchronous execution progress of dispatched CI/CD engineering remediations."""
        ...
