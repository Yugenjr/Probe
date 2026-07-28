"""Incident webhook reception endpoints."""
import uuid
from fastapi import APIRouter, BackgroundTasks, status
from ...schemas.webhooks import WebhookPayload, WebhookResponse
from ...models.incident import Incident, IncidentSeverity
from ...core.supervisor import CoreSupervisor

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


async def background_investigate(incident: Incident) -> None:
    """Asynchronous background execution handler running supervisor workflow loop."""
    supervisor = CoreSupervisor()
    await supervisor.initiate_investigation(incident)


@router.post(
    "",
    response_model=WebhookResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Receive anomaly event payload and trigger autonomous investigation",
)
async def receive_webhook(payload: WebhookPayload, background_tasks: BackgroundTasks) -> WebhookResponse:
    """Accept incoming anomaly event notifications from DriftGuard or monitoring platforms."""
    incident_id = f"inc-{uuid.uuid4().hex[:8]}"
    inv_id = f"inv-{incident_id}"

    incident = Incident(
        incident_id=incident_id,
        model_id=payload.model_id,
        model_version=payload.model_version,
        trigger_type=payload.event_type,
        severity=IncidentSeverity.MEDIUM,
        raw_payload=payload.model_dump(mode="json"),
    )

    # Dispatch non-blocking reasoning execution loop to background task queue
    background_tasks.add_task(background_investigate, incident)

    return WebhookResponse(
        investigation_id=inv_id,
        status="ACCEPTED",
        message="Investigation workflow dispatched asynchronously.",
    )
