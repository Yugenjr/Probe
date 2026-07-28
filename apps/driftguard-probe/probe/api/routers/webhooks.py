"""Incident webhook reception endpoints."""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from ...schemas.webhooks import WebhookPayload, WebhookResponse
from ...services.investigation_service import get_investigation_service, InvestigationService
from ...services.driftguard_client import (
    DriftGuardAuthenticationError,
    DriftGuardNotFoundError,
    DriftGuardServerError,
    DriftGuardConnectionError,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


@router.post(
    "",
    response_model=WebhookResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Receive anomaly event payload and trigger autonomous investigation",
)
async def receive_webhook(
    payload: WebhookPayload,
    investigation_service: InvestigationService = Depends(get_investigation_service)
) -> WebhookResponse:
    """Accept incoming anomaly event notifications from DriftGuard or monitoring platforms."""
    try:
        session = await investigation_service.create_from_webhook(payload)
    except DriftGuardAuthenticationError as e:
        logger.warning("Authentication failure with SDK during webhook execution: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Unauthorized: SDK authentication failed."
        )
    except DriftGuardNotFoundError as e:
        logger.warning("Resource not found in SDK during webhook execution: %s", e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Not Found: Model or resource not found on SDK."
        )
    except DriftGuardServerError as e:
        logger.error("Internal Server Error reported by SDK during webhook execution: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: SDK reported server failure."
        )
    except DriftGuardConnectionError as e:
        logger.error("Connection failure calling SDK during webhook execution: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service Unavailable: SDK connection failed."
        )
    except Exception as exc:
        logger.error("Unknown error occurred during webhook execution: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error: Unknown error during SDK integration."
        )

    return WebhookResponse(
        investigation_id=session.session_id,
        status="ACCEPTED",
        message="Investigation workflow dispatched asynchronously.",
    )
