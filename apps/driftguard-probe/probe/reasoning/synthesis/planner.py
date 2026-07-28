from enum import Enum
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from probe.context.models import InvestigationContext
from probe.storage.repository import EvidenceRepository
from probe.graph.builder import GraphTopology

class ReasoningStrategy(str, Enum):
    DISTRIBUTION_REASONING = "DISTRIBUTION_REASONING"      # Feature drift & demographic shift
    TEMPORAL_REASONING = "TEMPORAL_REASONING"              # Latency spikes & timing timeouts
    PREDICTION_REASONING = "PREDICTION_REASONING"          # Accuracy collapse & concept drift
    VALIDATION_REASONING = "VALIDATION_REASONING"          # Retraining challenger failures
    MULTI_MODAL_CORRELATION = "MULTI_MODAL_CORRELATION"    # Compound multi-system anomalies
    INSUFFICIENT_DATA_STRATEGY = "INSUFFICIENT_DATA_STRATEGY"  # Missing or disconnected graph

class ReasoningPlan(BaseModel):
    """
    Immutable reasoning execution plan generated prior to LLM synthesis.
    Prevents bloated monolith prompts by tailoring cognitive focus to the empirical anomaly type.
    """
    investigation_id: str
    strategy: ReasoningStrategy
    primary_evidence_types: List[str] = Field(default_factory=list)
    focus_metrics: List[str] = Field(default_factory=list)
    rationale: str
    instructions_summary: str

    class Config:
        frozen = True

class ReasoningPlanner:
    """
    Inspects the topological evidence graph and domain telemetry to select the optimal
    reasoning strategy BEFORE invoking CausalSynthesisAgent.
    Operates via deterministic rule evaluation without LLM dependency or prompt overhead.
    """
    @classmethod
    def create_plan(
        cls,
        investigation_id: str,
        context: InvestigationContext,
        topology: GraphTopology,
        repository: EvidenceRepository
    ) -> ReasoningPlan:
        nodes = topology.nodes
        if not nodes:
            return ReasoningPlan(
                investigation_id=investigation_id,
                strategy=ReasoningStrategy.INSUFFICIENT_DATA_STRATEGY,
                primary_evidence_types=[],
                focus_metrics=[],
                rationale="Zero nodes found in Evidence Graph topology.",
                instructions_summary="Abort generative synthesis; output 'Insufficient Evidence' artifact immediately."
            )

        # Count evidence occurrences by domain type
        counts: Dict[str, int] = {}
        for node in nodes:
            counts[node.evidence_type] = counts.get(node.evidence_type, 0) + 1

        has_drift = counts.get("DriftEvidence", 0) > 0
        has_validation = counts.get("ValidationEvidence", 0) > 0 or counts.get("RetrainingEvidence", 0) > 0
        has_metric = counts.get("MetricEvidence", 0) > 0
        has_model = counts.get("ModelEvidence", 0) > 0

        # Check for explicit retraining validation failure
        is_validation_failure = False
        for ev in repository.get_by_investigation(investigation_id):
            if ev.type in ("ValidationEvidence", "RetrainingEvidence"):
                if str(ev.payload.get("status", "")).lower() == "failed" or "error" in ev.payload:
                    is_validation_failure = True

        # Determine Strategy Hierarchy
        if is_validation_failure and not has_drift:
            strategy = ReasoningStrategy.VALIDATION_REASONING
            rationale = "Retraining pipeline or candidate challenger validation failed during evaluation."
            primary = ["ValidationEvidence", "RetrainingEvidence", "ModelEvidence"]
            instructions = "Focus exclusively on evaluation confusion metrics and challenger test suite rejections."
        elif has_drift and has_validation and is_validation_failure:
            strategy = ReasoningStrategy.MULTI_MODAL_CORRELATION
            rationale = "Concurrent observed statistical concept drift combined with automated retraining pipeline failure."
            primary = ["DriftEvidence", "ValidationEvidence", "RetrainingEvidence", "ModelEvidence", "AuditEvidence"]
            instructions = "Correlate feature distribution shift against downstream challenger evaluation collapse."
        elif has_drift:
            strategy = ReasoningStrategy.DISTRIBUTION_REASONING
            rationale = "Statistical covariate shift or feature distribution anomaly detected in inference telemetry."
            primary = ["DriftEvidence", "ModelEvidence", "PredictionEvidence"]
            instructions = "Focus on feature histograms, p-value divergences, and reference dataset drift thresholds."
        elif has_metric and not has_drift:
            strategy = ReasoningStrategy.TEMPORAL_REASONING
            rationale = "Infrastructure latency histograms or prediction volume throughput deviation detected."
            primary = ["MetricEvidence", "TelemetryEvidence", "ModelEvidence"]
            instructions = "Focus on temporal timing logs, DB commit latencies, and API throughput degradation."
        else:
            strategy = ReasoningStrategy.PREDICTION_REASONING
            rationale = "General model health degradation or accuracy decline without explicit covariate drift."
            primary = ["ModelEvidence", "PredictionEvidence", "AuditEvidence"]
            instructions = "Evaluate classification error rates and conceptual target shift over historical windows."

        focus = list(context.model.get("features", [])) + ["drift_score", "accuracy", "commit_latency"]
        return ReasoningPlan(
            investigation_id=investigation_id,
            strategy=strategy,
            primary_evidence_types=primary,
            focus_metrics=focus,
            rationale=rationale,
            instructions_summary=instructions
        )
