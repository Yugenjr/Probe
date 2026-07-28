"""Analytical tool capabilities invokable exclusively by autonomous reasoning expert agents."""
from .base import BaseTool
from .analytics import AnalyzeFeatureDriftTool, CorrelateLatencyWithDriftTool
from .forensic import FindSimilarHistoricalIncidentsTool, ValidateHypothesisTool, CompareModelVersionsTool
from .execution import EstimateRetrainingImpactTool, DispatchPipelineTool

# Backward-compatibility aliases for legacy imports and test harnesses
from .monitoring import (
    InspectModelMetadataTool,
    AnalyzeDriftDistributionTool,
    EvaluateMetricAnomaliesTool,
    VerifyValidationSuitabilityTool,
    AuditModelGovernanceTool,
    DispatchRetrainingPipelineTool,
)
from .driftguard import GetModelTool, GetMetricsTool, GetDriftTool, GetValidationTool, GetAuditTool, TriggerRetrainTool
from .history import SearchHistoryTool
from .docs import SearchDocsTool
from .experiment import RunExperimentTool
from .reports import GenerateReportTool

__all__ = [
    "BaseTool",
    # V2.0 Premier Analytical Tools
    "AnalyzeFeatureDriftTool",
    "CorrelateLatencyWithDriftTool",
    "FindSimilarHistoricalIncidentsTool",
    "ValidateHypothesisTool",
    "CompareModelVersionsTool",
    "EstimateRetrainingImpactTool",
    "DispatchPipelineTool",
    # Backward compatibility aliases
    "InspectModelMetadataTool",
    "AnalyzeDriftDistributionTool",
    "EvaluateMetricAnomaliesTool",
    "VerifyValidationSuitabilityTool",
    "AuditModelGovernanceTool",
    "DispatchRetrainingPipelineTool",
    "GetModelTool",
    "GetMetricsTool",
    "GetDriftTool",
    "GetValidationTool",
    "GetAuditTool",
    "TriggerRetrainTool",
    "SearchHistoryTool",
    "SearchDocsTool",
    "RunExperimentTool",
    "GenerateReportTool",
]
