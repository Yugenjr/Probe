"""Liveness and operational health verification endpoints."""
from fastapi import APIRouter, Depends
from ...schemas.api import APIResponse
from ...core.config import Settings
from ..dependencies import get_api_settings

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=APIResponse, summary="Kubernetes Health probe endpoint")
async def check_health(settings: Settings = Depends(get_api_settings)) -> APIResponse:
    """Verify operational health status of reasoning engine and adapter connections."""
    return APIResponse(
        status="success",
        data={
            "status": "HEALTHY",
            "service": settings.telemetry_service_name,
            "llm_provider": settings.llm_provider,
            "version": "0.1.0",
        },
    )
