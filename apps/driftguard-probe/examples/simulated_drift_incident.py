"""Example simulated anomaly execution triggering Probe investigation."""
import asyncio
import json
from probe.models.incident import Incident, IncidentSeverity
from probe.core.supervisor import CoreSupervisor


async def simulate_drift():
    """Simulate an incident webhook arriving from DriftGuard Platform."""
    print("--- [DriftGuard Platform] Detecting Feature Distribution Anomaly ---")
    webhook_payload = {
        "source_platform": "driftguard",
        "event_type": "drift_detected",
        "model_id": "fraud_detection_xgb",
        "model_version": "3.0.1",
        "details": {"feature": "transaction_velocity", "adwin_score": 0.15, "threshold": 0.08},
    }
    print("Dispatching webhook payload:")
    print(json.dumps(webhook_payload, indent=2))

    print("\n--- [DriftGuard Probe] Receiving Incident & Initiating Autonomous Investigation ---")
    incident = Incident(
        incident_id="inc-simulated-100",
        model_id=webhook_payload["model_id"],
        model_version=webhook_payload["model_version"],
        trigger_type=webhook_payload["event_type"],
        severity=IncidentSeverity.HIGH,
        raw_payload=webhook_payload,
    )

    supervisor = CoreSupervisor()
    state = await supervisor.initiate_investigation(incident)

    print("\n[Investigation Completed successfully!]")
    print(f"Investigation ID: {state.investigation_id}")
    print(f"Final Lifecycle State: {state.status.value}")
    print("Chronology History Trace:")
    for entry in state.execution_history:
        print(f" -> {entry}")


if __name__ == "__main__":
    asyncio.run(simulate_drift())
