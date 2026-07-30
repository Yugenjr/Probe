from .base import BaseAgent
import logging
from typing import List
from ..engine.state import InvestigationSession
from ..domain.evidence import CodeChangeEvidence
import uuid

logger = logging.getLogger(__name__)

class RepoAnalystAgent(BaseAgent):

    @property
    def role_name(self) -> str:
        return "RepoAnalyst"

    """Agent responsible for analyzing code, PRs, configurations, and releases."""
    
    async def execute(self, session: InvestigationSession) -> List[CodeChangeEvidence]:
        logger.info("RepoAnalystAgent analyzing repository changes for session %s", session.session_id)
        
        evidence = CodeChangeEvidence(
            evidence_id=str(uuid.uuid4()),
            source_provider="GitHubAdapter",
            retrieved_by_tool="RepoAnalystAgent",
            summary="Recent deployment of billing service included a new feature flag.",
            confidence_weight=0.9,
            relevance_score=0.85,
            change_type="deployment",
            author="deploy-bot",
            description="Production deployment of v2.4.1",
            diff_summary="Changes to feature flags and minor refactors."
        )
        
        return [evidence]
