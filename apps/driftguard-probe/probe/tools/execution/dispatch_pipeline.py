"""Execution tool initiating model retraining CI/CD jobs via segregated ExecutionProvider."""
from typing import Any, Dict, Optional
from ..base import BaseTool
from ...interfaces.execution import ExecutionProvider
from ...interfaces.context import ResourceContext


class DispatchPipelineTool(BaseTool):
    """Execution tool dispatching automated training or fallback rollback CI/CD pipeline remediations."""
    def __init__(self, provider: Optional[ExecutionProvider] = None, **kwargs: Any):
        super().__init__(**kwargs)
        self.provider = provider

    @property
    def name(self) -> str:
        return "dispatch_remediation_pipeline"

    @property
    def description(self) -> str:
        return "Dispatch automated training pipeline job or canary rollback remediation onto target deployment endpoints."

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "model_id": {"type": "string"},
                "action": {"type": "string", "default": "RETRAIN"},
            },
            "required": ["model_id"],
        }

    async def invoke(self, **kwargs: Any) -> Dict[str, Any]:
        provider = self.provider or self.container.execution_provider
        if not provider:
            raise RuntimeError("ExecutionProvider is not configured in Inversion of Control container.")
        
        target = ResourceContext(model_id=kwargs["model_id"])
        res = await provider.trigger_retraining(target, kwargs.get("dataset_path"))
        return {"dispatch_result": res, "pipeline_status": "DISPATCHED", "target_model": kwargs["model_id"]}
