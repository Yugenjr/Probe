import logging
import asyncio
from datetime import datetime, timezone
from typing import List
from ..engine.state import InvestigationSession
from ..domain.evidence import EvidenceBundle

logger = logging.getLogger(__name__)

class EvidenceCollector:
    """Service responsible for managing the concurrent execution of evidence agents and timeline compilation."""
    
    async def collect(self, session: InvestigationSession) -> EvidenceBundle:
        """Collects evidence in parallel from specialist agents, synthesizes a timeline, and returns an EvidenceBundle."""
        logger.info("EvidenceCollector starting collection for session %s", session.session_id)
        collection_started_at = datetime.now(timezone.utc)
        
        from ..agents.metrics import MetricAnalystAgent
        from ..agents.logs import LogForensicsAgent
        from ..agents.repo import RepoAnalystAgent
        from ..agents.researcher import ResearcherAgent
        from ..agents.timeline import TimelineAnalystAgent
        
        agents = {
            "MetricAnalystAgent": MetricAnalystAgent(),
            "LogForensicsAgent": LogForensicsAgent(),
            "RepoAnalystAgent": RepoAnalystAgent(),
            "ResearcherAgent": ResearcherAgent()
        }
        
        agent_names = list(agents.keys())
        tasks = [agent.execute(session) for agent in agents.values()]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_evidence = []
        failed_agents = []
        successful_agents = []
        
        for name, res in zip(agent_names, results):
            if isinstance(res, Exception):
                logger.error("Agent %s failed: %s", name, res)
                failed_agents.append(name)
            elif isinstance(res, list):
                all_evidence.extend(res)
                session.universal_evidence.extend(res)
                successful_agents.append(name)
        
        # Timeline compilation
        timeline_agent = TimelineAnalystAgent()
        try:
            bundle = await timeline_agent.execute(session, all_evidence)
        except Exception as e:
            logger.error("TimelineAnalystAgent failed: %s", e)
            failed_agents.append("TimelineAnalystAgent")
            # Create a fallback empty bundle
            from ..domain.evidence import EvidenceBundle
            bundle = EvidenceBundle()
            
        collection_finished_at = datetime.now(timezone.utc)
        duration = (collection_finished_at - collection_started_at).total_seconds()
        
        bundle.collection_started_at = collection_started_at
        bundle.collection_finished_at = collection_finished_at
        bundle.total_duration = duration
        bundle.failed_agents = failed_agents
        bundle.successful_agents = successful_agents
        
        if failed_agents:
            if successful_agents:
                bundle.status = "PARTIAL"
            else:
                bundle.status = "FAILED"
        else:
            bundle.status = "COMPLETE"
            
        session.evidence_bundle = bundle
        session.execution_history.append(
            f"[EvidenceCollector] Completed with status {bundle.status}. "
            f"Gathered {len(all_evidence)} items in {duration:.2f}s."
        )
        
        return bundle
