import datetime
from typing import Dict, List, Any, Optional
from probe.providers.base import ProviderAdapter
from probe.context.models import InvestigationContext

class ContextBuilder:
    """
    Consumes provider adapters and produces an immutable InvestigationContext.
    Its responsibility is ONLY to gather information.
    No reasoning. No confidence scoring. No recommendations. No hypothesis generation.
    """
    def __init__(self, adapter: ProviderAdapter):
        self._adapter = adapter

    def build_context(self, investigation_id: str, target_model_id: str, tenant_id: str = "default") -> InvestigationContext:
        now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        # 1. Fetch raw data across provider interface without knowing implementation details
        model_details = self._adapter.fetch_model_details(target_model_id)
        model_versions = self._adapter.fetch_model_versions(target_model_id)
        audit_logs = self._adapter.fetch_audit_logs(target_model_id)
        drift_logs = self._adapter.fetch_drift_history(target_model_id, limit=500)
        retrain_logs = self._adapter.fetch_retraining_history(target_model_id)
        metrics = self._adapter.fetch_system_metrics(target_model_id)

        # 2. Extract active version
        active_version = model_details.get("version", "")

        # 3. Identify incident trigger if available in audit ledger
        incident_event = {}
        for entry in audit_logs:
            if entry.get("event_type") == "drift_detected":
                incident_event = entry
                break

        # 4. Extract monitoring threshold rules
        monitor_rules = {
            "drift_threshold": model_details.get("drift_threshold", 0.15),
            "features_tracked": model_details.get("features", [])
        }

        # 5. Extract validation details from retraining candidate evaluations
        validation_info = {}
        if retrain_logs:
            latest_retrain = retrain_logs[0]
            validation_info = {
                "last_challenger": latest_retrain.get("new_version"),
                "validation_status": latest_retrain.get("status"),
                "old_accuracy": latest_retrain.get("old_accuracy"),
                "new_accuracy": latest_retrain.get("new_accuracy"),
                "error_reason": latest_retrain.get("details", {}).get("error")
            }

        # 6. Extract predictions array from historical drift logs
        predictions = [
            {
                "timestamp": d.get("timestamp"),
                "features": d.get("features"),
                "prediction": d.get("prediction"),
                "drift_score": d.get("drift_score")
            }
            for d in drift_logs
        ]

        # 7. Map relationships between objects
        relationships = {
            "model_to_versions": [v.get("version") for v in model_versions if v.get("version")],
            "incident_to_model": [target_model_id] if incident_event else []
        }

        # 8. Synthesize immutable context
        return InvestigationContext(
            investigation_id=investigation_id,
            tenant_id=tenant_id,
            timestamp_utc=now_utc,
            provider_name=self._adapter.provider_name,
            incident=incident_event,
            model=model_details,
            model_version=active_version,
            monitor=monitor_rules,
            drift={"records": drift_logs, "overall_status": model_details.get("status")},
            validation=validation_info,
            audit=audit_logs,
            retraining=retrain_logs,
            telemetry=metrics,
            predictions=predictions,
            reports=[],
            metadata={"reference_data": model_details.get("reference_data_path", "")},
            relationships=relationships
        )
