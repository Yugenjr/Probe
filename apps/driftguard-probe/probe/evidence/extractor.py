from typing import List, Dict, Any
from probe.context.models import InvestigationContext
from probe.evidence.base import (
    Evidence, DriftEvidence, ValidationEvidence, AuditEvidence,
    TelemetryEvidence, MetricEvidence, ModelEvidence, RetrainingEvidence,
    PredictionEvidence, ReportEvidence
)

class EvidenceExtractor:
    """
    Consumes an immutable InvestigationContext and outputs deterministic typed Evidence objects.
    Guarantees idempotency: running extraction twice produces exactly identical Evidence IDs and SHA-256 hashes.
    No LLM hallucination or generative prompts involved.
    """
    def extract_all_evidence(self, context: InvestigationContext) -> List[Evidence]:
        evidence_registry: List[Evidence] = []
        provider = context.provider_name
        origin = context.investigation_id

        # 1. ModelEvidence
        model_ev: Optional[ModelEvidence] = None
        if context.model:
            model_ev = ModelEvidence.generate_deterministic(
                type="ModelEvidence",
                provider=provider,
                timestamp=context.timestamp_utc,
                source=f"model/{context.model.get('model_id', 'unknown')}",
                payload={"model_details": context.model, "version": context.model_version},
                confidence=0.95,
                relationships=[],
                origin=origin
            )
            evidence_registry.append(model_ev)

        model_ref = [model_ev.id] if model_ev else []

        # 2. DriftEvidence
        drift_records = context.drift.get("records", [])
        drift_ids = []
        for d in drift_records:
            d_ev = DriftEvidence.generate_deterministic(
                type="DriftEvidence",
                provider=provider,
                timestamp=d.get("timestamp", context.timestamp_utc),
                source="drift_telemetry_stream",
                payload={"drift_score": d.get("drift_score"), "features": d.get("features")},
                confidence=0.90,
                relationships=model_ref,
                origin=origin
            )
            evidence_registry.append(d_ev)
            drift_ids.append(d_ev.id)

        # 3. AuditEvidence
        for a in context.audit:
            a_ev = AuditEvidence.generate_deterministic(
                type="AuditEvidence",
                provider=provider,
                timestamp=a.get("timestamp", context.timestamp_utc),
                source=f"audit/{a.get('event_type')}",
                payload={"details": a},
                confidence=0.95,
                relationships=model_ref + drift_ids[:2], # Cross link with active drift anomalies
                origin=origin
            )
            evidence_registry.append(a_ev)

        # 4. RetrainingEvidence & ValidationEvidence
        for r in context.retraining:
            r_ev = RetrainingEvidence.generate_deterministic(
                type="RetrainingEvidence",
                provider=provider,
                timestamp=r.get("start_time", context.timestamp_utc),
                source=f"retraining/{r.get('id')}",
                payload={"retraining_execution": r},
                confidence=0.90,
                relationships=model_ref,
                origin=origin
            )
            evidence_registry.append(r_ev)
            
            # Extract ValidationEvidence from retraining candidate challenger evaluation
            v_ev = ValidationEvidence.generate_deterministic(
                type="ValidationEvidence",
                provider=provider,
                timestamp=r.get("start_time", context.timestamp_utc),
                source="validation_challenger_verdict",
                payload={
                    "old_accuracy": r.get("old_accuracy"),
                    "new_accuracy": r.get("new_accuracy"),
                    "status": r.get("status"),
                    "error": r.get("details", {}).get("error")
                },
                confidence=0.92,
                relationships=[r_ev.id] + model_ref,
                origin=origin
            )
            evidence_registry.append(v_ev)

        # 5. MetricEvidence
        for m in context.telemetry:
            m_ev = MetricEvidence.generate_deterministic(
                type="MetricEvidence",
                provider=provider,
                timestamp=context.timestamp_utc,
                source=m.get("metric_name", "prom_metric"),
                payload=m,
                confidence=0.85,
                relationships=model_ref,
                origin=origin
            )
            evidence_registry.append(m_ev)

        return evidence_registry
