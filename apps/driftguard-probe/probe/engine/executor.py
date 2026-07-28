"""AgentExecutor governing lifecycle, tracking, and metric recording of individual agent executions."""
import time
import logging
from typing import Any, Optional
from .registry import get_agent_registry
from ..engine.state import InvestigationSession
from ..storage.session_repository import get_session_repository
from ..events.publisher import EventPublisher
from ..events.models import EventType

logger = logging.getLogger(__name__)


class AgentExecutor:
    """Standardized wrapper executing individual agents within the runtime context.
    
    Ensures all agent runs are wrapped with standardized logging, duration metrics,
    exception handling, session updates, and event publishing.
    """

    def __init__(self, registry=None, session_repo=None):
        self.registry = registry or get_agent_registry()
        self.session_repo = session_repo or get_session_repository()
        self.publisher = EventPublisher(source_module="probe.engine.executor")

    async def execute(self, role_name: str, session: InvestigationSession, **kwargs: Any) -> Any:
        """Instantiate and execute the target agent, tracking lifecycle details and updating the session."""
        logger.info("Executor activating agent '%s' for session %s", role_name, session.session_id)
        from datetime import datetime, timezone
        from ..engine.state import AgentResult
        from ..core.di import get_container
        from ..llm.providers import get_llm_provider
        
        # 1. Resolve agent class from registry
        agent_class = self.registry.get(role_name)
        
        # 2. Instantiate agent injecting LLM provider from DI/factory
        container = get_container()
        if not container.llm_provider:
            container.llm_provider = get_llm_provider()
        agent = agent_class(llm_provider=container.llm_provider)

        # 3. Publish AGENT_ACTIVATED lifecycle event
        await self.publisher.emit(
            event_type=EventType.AGENT_ACTIVATED,
            investigation_id=session.session_id,
            attributes={"role": role_name}
        )

        started_at = datetime.now(timezone.utc)
        start_time = time.perf_counter()
        
        try:
            # 4. Execute agent logic
            result = await agent.execute(session, **kwargs)
            duration = time.perf_counter() - start_time
            finished_at = datetime.now(timezone.utc)
            
            # 5. Record standardized AgentResult payload
            agent_result = AgentResult(
                agent_name=role_name,
                started_at=started_at,
                finished_at=finished_at,
                success=True,
                output=result,
                latency=duration,
                metadata={}
            )
            session.agent_results.append(agent_result)
            
            # 6. Record telemetry log to execution history
            session.execution_history.append(
                f"[Agent Executor] Executed '{role_name}' successfully in {duration:.3f}s."
            )
            
            # 7. Save updated session state
            await self.session_repo.save(session)
            
            logger.info("Agent '%s' completed successfully in %.3fs", role_name, duration)
            return agent_result
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            finished_at = datetime.now(timezone.utc)
            
            # Record failed AgentResult
            agent_result = AgentResult(
                agent_name=role_name,
                started_at=started_at,
                finished_at=finished_at,
                success=False,
                output=None,
                latency=duration,
                metadata={"error": str(e)}
            )
            session.agent_results.append(agent_result)
            
            session.execution_history.append(
                f"[Agent Executor] Agent '{role_name}' failed after {duration:.3f}s: {e}"
            )
            await self.session_repo.save(session)
            logger.error("Agent '%s' failed during execution: %s", role_name, e, exc_info=True)
            raise e
