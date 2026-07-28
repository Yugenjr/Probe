# Integration Architecture: DriftGuard Probe & DriftGuard SDK

## Phase 1: SDK Architecture Inspection

### Core Components
1. **REST API**: Exposes all endpoints via FastAPI, running in `packages/driftguard-sdk/main.py`. The routing is split into `routers/` (e.g. `models.py`, `telemetry.py`, `audit.py`).
2. **Evidently Service**: Evidently is **not** a standalone service. It runs embedded directly within the SDK API container via an isolated route at `routers/evidently.py` (`POST /evidently/calculate`).
3. **Dashboard Backend**: The dashboard is a standalone **Next.js** application located in `packages/driftguard-sdk/dashboard`. It interacts directly with the SDK REST API.

---

## Phase 2: Startup Commands

To start the entire underlying SDK infrastructure, use the following commands in separate terminals:

### Terminal 1 (SDK API + Evidently)
```bash
cd packages/driftguard-sdk
# Activate virtual environment if applicable
pip install -r requirements.txt
pip install -e .
# Start the FastAPI server
uvicorn main:app --port 8000 --reload
# Expected Port: 8000
# Expected URL: http://localhost:8000
```

### Terminal 2 (Dashboard)
```bash
cd packages/driftguard-sdk/dashboard
npm install
npm run dev
# Expected Port: Typically 3001 or 3000
```
*(Note: There is no separate command for Evidently, as it is bundled inside Terminal 1).*

---

## Phase 3: Authentication Design

- **Generation**: API keys are generated via the `POST /users/register` endpoint or at startup for the default admin via `secrets.token_hex(16)`.
- **Storage**: Only the SHA-256 hash of the API key is stored in the database (`DBUser.api_key_hash`). The plain text is never stored.
- **Validation**: Incoming requests are validated by comparing the SHA-256 hash of the header key against the database.
- **Middleware**: A FastAPI HTTP middleware `api_key_auth_middleware` intercepts all traffic.
- **Protected Endpoints**: All endpoints require authentication EXCEPT `/health`, `/api/health`, `/docs`, `/openapi.json`, `/users/register`, and `/metrics`.
- **Header Structure**: Clients must pass the token in the `X-API-Key` header.

---

## Phase 4: Probe Client Design

The `DriftGuardClient` should reside within the Probe application at:
`apps/driftguard-probe/probe/clients/driftguard_client.py` (or a similar `clients/` module).

### Responsibilities:
- Manage the `API_URL` and `X-API-Key`.
- Expose typed Python methods mapping to the existing REST API.

### Required Endpoints to Consume:
- `get_models()` -> `GET /models`
- `get_model(model_id)` -> `GET /models/{model_id}`
- `get_audit_logs(model_id)` -> `GET /audit/{model_id}`
- `get_model_health(model_id)` -> `GET /models/{model_id}`

*(Note: `get_predictions`, `get_drift_status`, and `get_recent_metrics` are all combined under a single endpoint, detailed below).*

---

## Phase 5: Telemetry Flow

**Architecture**: The SDK uses a **Push** architecture. Machine learning pipelines (or inference servers) `POST` to `/predict/{model_id}` to push features, predictions, and drift scores.
**Storage**: Telemetry is stored directly in the `dg_predictions` relational table (Postgres/SQLite).
**Metrics**: The SDK actively formats Prometheus metrics at `/metrics` via `drift_gauge`, `accuracy_gauge`, etc.

### Telemetry Retrieval by Probe
Probe will **Pull** the latest telemetry using a single unified endpoint:
`GET /drift/{model_id}`

This endpoint natively returns a historical list of up to 500 records containing:
- **Drift Score**: `drift_score`
- **Prediction Volume**: Implicit via the length of the returned array.
- **Feature Drift**: Available inside the `features` JSON payload in the response.
- **Target Drift**: Available inside the `prediction` JSON payload.
- **Last Prediction Time**: `timestamp` field of the first array item.
- **Status/Alerts**: Alerts are triggered automatically during the push phase via `send_alert` inside `telemetry.py`.

### Missing Telemetry
> [!WARNING]
> **Latency** and **Last Drift Detection Time** are NOT explicitly returned by `GET /drift/{model_id}`. Latency is only tracked via Prometheus histograms, and detection time requires parsing the `/audit/{model_id}` logs for `event_type="drift_detected"`. Probe will need to cross-reference the audit endpoint.

---

## Phase 6: Investigation Trigger Flow

1. **User opens Probe**
2. **Authenticate**: Probe backend authenticates against SDK via `X-API-Key`.
3. **Fetch accessible models**: `GET /models`
4. **Display model list**: Rendered in UI.
5. **User selects model**: Click event.
6. **Fetch latest telemetry**: Parallel calls to `GET /drift/{model_id}` and `GET /audit/{model_id}`.
7. **Create Investigation Context**: Combine drift arrays, audit logs, and status.
8. **Pass context to Supervisor Agent**: The LLM analyzes the context to explain the drift.

---

## Phase 7: Environment Variables

Probe will need the following `.env` variables to operate the `DriftGuardClient`:
```env
DRIFTGUARD_API_URL=http://localhost:8000
DRIFTGUARD_API_KEY=dg-<your-key>
```
