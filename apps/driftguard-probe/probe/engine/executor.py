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
        from ..llm.service import get_llm_service
        
        # 1. Resolve agent class from registry
        agent_class = self.registry.get(role_name)
        
        # 2. Instantiate agent injecting LLM service and ToolGateway from DI container
        container = get_container()
        if not container.llm_provider:
            container.llm_provider = get_llm_service()
        agent = agent_class(
            llm_provider=container.llm_provider,
            tool_gateway=getattr(container, "tool_gateway", None),
            evidence_gateway=getattr(container, "evidence_gateway", None),
        )


        # 3. Publish AGENT_ACTIVATED lifecycle event
        await self.publisher.emit(
            event_type=EventType.AGENT_ACTIVATED,
            investigation_id=session.session_id,
            attributes={"role": role_name}
        )

        started_at = datetime.now(timezone.utc)
        
        import asyncio
        
        max_retries = kwargs.get("max_retries", 3)
        timeout_seconds = kwargs.get("timeout_seconds", 30.0)
        
        retry_count = 0
        last_error = None
        duration = 0.0
        success = False
        result = None
        
        while retry_count < max_retries:
            start_time = time.perf_counter()
            try:
                # 4. Execute agent logic with timeout
                result = await asyncio.wait_for(agent.execute(session, **kwargs), timeout=timeout_seconds)
                duration = time.perf_counter() - start_time
                success = True
                break
            except asyncio.TimeoutError as te:
                retry_count += 1
                last_error = f"Agent execution timed out after {timeout_seconds}s"
                duration = time.perf_counter() - start_time
                logger.warning("Agent '%s' execution timed out (try %d/%d)", role_name, retry_count, max_retries)
            except Exception as e:
                retry_count += 1
                last_error = str(e)
                duration = time.perf_counter() - start_time
                logger.warning("Agent '%s' execution failed: %s (try %d/%d)", role_name, e, retry_count, max_retries)
                if retry_count < max_retries:
                    # Short backoff to keep tests quick
                    await asyncio.sleep(0.1 * (2 ** (retry_count - 1)))
        
        finished_at = datetime.now(timezone.utc)
        
        # 5. Extract Reasoning Trace if populated
        metadata = {}
        if hasattr(container.llm_provider, "last_trace") and container.llm_provider.last_trace:
            metadata["reasoning_trace"] = container.llm_provider.last_trace
            container.llm_provider.last_trace = None

        if not success:
            metadata["error"] = last_error
            # Record failed AgentResult
            agent_result = AgentResult(
                agent_name=role_name,
                started_at=started_at,
                finished_at=finished_at,
                success=False,
                output=None,
                latency=duration,
                metadata=metadata,
                retries=retry_count
            )
            session.agent_results.append(agent_result)
            session.execution_history.append(
                f"[Agent Executor] Executed '{role_name}' failed after {retry_count} tries: {last_error}"
            )
            await self.session_repo.save(session)
            raise RuntimeError(f"Agent '{role_name}' failed after {max_retries} attempts. Last error: {last_error}")
            
        # 6. Record successful AgentResult payload
        tokens = 0
        cost = 0.0
        if "reasoning_trace" in metadata:
            tokens = metadata["reasoning_trace"].get("total_tokens", 0)
            cost = metadata["reasoning_trace"].get("cost_estimate", 0.0)

        agent_result = AgentResult(
            agent_name=role_name,
            started_at=started_at,
            finished_at=finished_at,
            success=True,
            output=result,
            latency=duration,
            metadata=metadata,
            tokens=tokens,
            cost=cost,
            retries=retry_count
        )
        session.agent_results.append(agent_result)
        
        # 7. Record telemetry log to execution history
        session.execution_history.append(
            f"[Agent Executor] Executed '{role_name}' successfully in {duration:.3f}s (tries: {retry_count if retry_count > 0 else 1})."
        )
        
        # 8. Save updated session state
        await self.session_repo.save(session)
        
        logger.info("Agent '%s' completed successfully in %.3fs", role_name, duration)
        return agent_result
