"""Deprecated backwards-compatibility aliases for legacy tool naming."""
import warnings
from .monitoring import (
    InspectModelMetadataTool as GetModelTool,
    EvaluateMetricAnomaliesTool as GetMetricsTool,
    AnalyzeDriftDistributionTool as GetDriftTool,
    VerifyValidationSuitabilityTool as GetValidationTool,
    AuditModelGovernanceTool as GetAuditTool,
    DispatchRetrainingPipelineTool as TriggerRetrainTool,
)

warnings.warn(
    "probe.tools.driftguard is deprecated and will be removed in v1.0. Import analytical tools from probe.tools.monitoring.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "GetModelTool",
    "GetMetricsTool",
    "GetDriftTool",
    "GetValidationTool",
    "GetAuditTool",
    "TriggerRetrainTool",
]
