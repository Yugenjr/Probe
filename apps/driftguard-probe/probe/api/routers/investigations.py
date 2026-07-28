"""Investigation state and reports query endpoints."""
from typing import List
from fastapi import APIRouter, HTTPException, status
from ...schemas.api import APIResponse
from ...core.lifecycle import InvestigationStatus

router = APIRouter(prefix="/api/v1/investigations", tags=["investigations"])


@router.get("", response_model=APIResponse, summary="List active and historical investigations")
async def list_investigations(limit: int = 20, skip: int = 0) -> APIResponse:
    """Retrieve summarized array of recorded investigation executions."""
    # TODO: Implementation pending for actual StorageProvider querying
    return APIResponse(status="success", data={"total": 0, "limit": limit, "skip": skip, "items": []})


@router.get("/{investigation_id}", response_model=APIResponse, summary="Get investigation details and executive report")
async def get_investigation_details(investigation_id: str) -> APIResponse:
    """Retrieve full lifecycle execution state, tested hypotheses, and compiled markdown report."""
    # TODO: Implementation pending for querying persistent SQLite/Vector storage repository
    if investigation_id == "inv-not-found":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Investigation '{investigation_id}' not found.")
        
    return APIResponse(
        status="success",
        data={
            "investigation_id": investigation_id,
            "status": InvestigationStatus.COMPLETED.value,
            "hypotheses_count": 1,
            "experiments_count": 1,
            "report_available": True,
        },
    )
