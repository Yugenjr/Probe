# DriftGuard SDK

The `driftguard-sdk` package is the core shared runtime, monitoring, and validation framework used by both Decision Probe and DriftGuard Probe.

## Purpose
To provide a standardized, reusable infrastructure layer that prevents code duplication across the Probe ecosystem. It establishes the canonical database schema, exposes the primary API gateway for model registration, and manages the ingestion of real-time telemetry.

## Architecture & Reusable Modules
The SDK is built around a robust `main.py` FastAPI application which handles:
- **Authentication**: Custom API key hashing and middleware (`X-API-Key` validation).
- **Database Schema (SQLAlchemy)**: Defines standard entities like `DBUser`, `DBProject`, `DBModel`, `DBModelVersion`, `DBPredictionLog`, `DBRetrainingEvent`, and `DBAuditLogEntry`. It natively supports PostgreSQL with an automatic fallback to local SQLite for easy development.
- **Observability (Prometheus)**: Exposes standard metrics (`driftguard_predictions_total`, `driftguard_drift_score`, `driftguard_model_accuracy`, `driftguard_retraining_triggered_total`, `driftguard_inference_latency_seconds`).
- **Webhooks**: Handles the dispatching of webhooks to external orchestrators (like Airflow) when a retraining event is triggered.

## Public APIs
Key REST endpoints exposed by the SDK gateway:
- `POST /users/register`: Create a new API user.
- `POST /register`: Register a new ML model for tracking, setting drift thresholds and baselines.
- `POST /retrain/{model_id}`: Trigger the retraining flow asynchronously. Creates event locks in the database to prevent concurrent retraining race conditions.
- `POST /retrain/{model_id}/complete`: Callback endpoint for SDK callback pipelines to report validation results and promote challenger models.

## Dependency Graph & Consumption
- Both `apps/decision-probe` and `apps/driftguard-probe` rely on this SDK for standard database connections and metrics.
- Applications import directly from `driftguard-sdk` or send REST requests to its exposed gateway port.
- Designed with extensibility in mind, allowing the swap of the underlying SQL engine without impacting the agent layer in `driftguard-probe`.
