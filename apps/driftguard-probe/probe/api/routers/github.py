from fastapi import APIRouter
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/github", tags=["GitHub"])

class GitHubStats(BaseModel):
    stars: int
    open_issues: int
    latest_commit: str

@router.get("/stats", response_model=GitHubStats)
async def get_github_stats():
    return GitHubStats(
        stars=120,
        open_issues=5,
        latest_commit="Update billing service feature flags"
    )
