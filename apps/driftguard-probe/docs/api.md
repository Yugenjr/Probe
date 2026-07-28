# API Reference Guide

The Probe gateway runs on FastAPI, providing asynchronous routing for incident webhook processing and inspection queries.

## Webhooks Endpoint
### `POST /api/v1/webhooks`
Accepts standardized incident event payloads from monitored platforms and initiates an asynchronous investigation workflow.
- **Payload Schema**: `probe.schemas.webhooks.WebhookPayload`
- **Returns**: `202 Accepted` containing the assigned `investigation_id`.

## Investigations Query Endpoints
### `GET /api/v1/investigations/{id}`
Returns the current execution state, active lifecycle phase, and accumulated evidence for an ongoing or completed investigation.
- **Response Schema**: `probe.models.investigation.Investigation`

### `GET /api/v1/investigations`
List historical investigations filtered by model ID, status, or date range.

## Health Verification
### `GET /api/v1/health`
Kubernetes liveness and readiness probes verifying LLM connectivity, database readiness, and adapter status.
