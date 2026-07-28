"""Investigation state and reports query endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from ...schemas.api import APIResponse
from ...storage.session_repository import get_session_repository, SessionRepository

router = APIRouter(prefix="/api/v1/investigations", tags=["investigations"])


@router.get("", response_model=APIResponse, summary="List active and historical investigations")
async def list_investigations(
    limit: int = 20,
    skip: int = 0,
    session_repo: SessionRepository = Depends(get_session_repository)
) -> APIResponse:
    """Retrieve summarized array of recorded investigation executions."""
    if hasattr(session_repo, "_storage"):
        sessions = list(session_repo._storage.values())
        items = [s.model_dump(mode="json") for s in sessions[skip:skip+limit]]
        total = len(sessions)
    else:
        items = []
        total = 0
    return APIResponse(status="success", data={"total": total, "limit": limit, "skip": skip, "items": items})


@router.get("/{investigation_id}", response_model=APIResponse, summary="Get investigation details and executive report")
async def get_investigation_details(
    investigation_id: str,
    session_repo: SessionRepository = Depends(get_session_repository)
) -> APIResponse:
    """Retrieve full lifecycle execution state, tested hypotheses, and compiled markdown report."""
    session = await session_repo.get(investigation_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Investigation '{investigation_id}' not found."
        )
    return APIResponse(
        status="success",
        data=session.model_dump(mode="json")
    )
