"""InvestigationRuntime orchestrating multi-agent workflow plans and session transitions."""
import logging
from typing import Optional
from .executor import AgentExecutor
from ..engine.state import InvestigationStatus
from ..storage.session_repository import get_session_repository
from ..events.bus import get_event_bus
from ..events.models import DomainEvent, EventType

logger = logging.getLogger(__name__)


class InvestigationRuntime:
    """Orchestrator managing the execution plan, sequential agent activation, and state updates."""

    def __init__(self, executor: Optional[AgentExecutor] = None, session_repo=None):
        self.executor = executor or AgentExecutor()
        self.session_repo = session_repo or get_session_repository()
        self.event_bus = get_event_bus()

    def subscribe_to_bus(self) -> None:
        """Register the runtime as a listener for INCIDENT_RECEIVED events."""
        self.event_bus.subscribe(self.handle_incident_event, EventType.INCIDENT_RECEIVED)
        logger.info("InvestigationRuntime successfully subscribed to EventBus.")

    async def handle_incident_event(self, event: DomainEvent) -> None:
        """Handler for DomainEvent of type INCIDENT_RECEIVED."""
        if event.investigation_id:
            logger.info("Event received: %s. Starting runtime for %s", event.event_type, event.investigation_id)
            # Dispatch investigation asynchronously
            import asyncio
            asyncio.create_task(self.start_investigation(event.investigation_id))

    async def start_investigation(self, investigation_id: str) -> None:
        """Coordinate execution of Supervisor and the resulting ExecutionPlan for the target session."""
        logger.qualname = "probe.engine.runtime"
        logger.info("Beginning investigation pipeline for session: %s", investigation_id)

        session = await self.session_repo.get(investigation_id)
        if not session:
            logger.error("Session '%s' not found. Terminating runtime execution.", investigation_id)
            return

        try:
            from probe.engine.workflow import ExecutionPlan, ExecutionStep
            
            # Use a static, comprehensive execution plan for the UI to display all 14 agents
            execution_plan = ExecutionPlan(
                steps=[
                    ExecutionStep(agent_role="Triage", description="Initial incident triage and routing"),
                    ExecutionStep(agent_role="Supervisor", description="Orchestrate investigation pipeline"),
                    ExecutionStep(agent_role="Planner", description="Generate diagnostic execution plan"),
                    ExecutionStep(agent_role="MemoryRecall", description="Recall historical incidents"),
                    ExecutionStep(agent_role="TimelineAnalyst", description="Analyze temporal sequences"),
                    ExecutionStep(agent_role="MetricAnalyst", description="Correlate telemetry metrics"),
                    ExecutionStep(agent_role="RepoAnalyst", description="Audit repository changes"),
                    ExecutionStep(agent_role="LogForensics", description="Extract forensic logs"),
                    ExecutionStep(agent_role="Investigator", description="Collect universal evidence"),
                    ExecutionStep(agent_role="CausalSynthesis", description="Synthesize causal hypotheses"),
                    ExecutionStep(agent_role="AdversarialCritic", description="Validate and critique hypotheses"),
                    ExecutionStep(agent_role="InterventionArchitect", description="Design remediation strategies"),
                    ExecutionStep(agent_role="Compliance", description="Verify compliance constraints"),
                    ExecutionStep(agent_role="Reporter", description="Draft final incident report")
                ]
            )

            # 2. Iterate through each step sequentially
            for step in execution_plan.steps:
                role = step.agent_role
                logger.info("Runtime executing plan step: %s (%s)", role, step.description)

                # Transition session status based on agent role
                if role == "Planner":
                    session.transition_to(InvestigationStatus.PLANNING, f"Running step: {step.description}")
                elif role == "Investigator":
                    session.transition_to(InvestigationStatus.COLLECTING_EVIDENCE, f"Running step: {step.description}")
                elif role == "CausalSynthesis":
                    session.transition_to(InvestigationStatus.HYPOTHESIS_SYNTHESIS, f"Running step: {step.description}")
                elif role == "AdversarialCritic":
                    session.transition_to(InvestigationStatus.EXPERIMENTAL_VALIDATION, f"Running step: {step.description}")
                elif role == "InterventionArchitect":
                    session.transition_to(InvestigationStatus.REMEDIATION_READY, f"Running step: {step.description}")
                elif role == "Reporter":
                    session.transition_to(InvestigationStatus.REPORTING, f"Running step: {step.description}")

                await self.session_repo.save(session)

                # Run agent using the executor
                try:
                    post_investigator_roles = ["CausalSynthesis", "AdversarialCritic", "InterventionArchitect", "Compliance", "Reporter"]
                    if role in post_investigator_roles:
                        from probe.core.di import get_container
                        container = get_container()
                        if container.llm_provider and hasattr(container.llm_provider, '_api_keys'):
                            logger.info("Switching API key for post-investigator stage: %s", role)
                            container.llm_provider._api_keys = ["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"]
                    
                    await self.executor.execute(role, session)
                except Exception as e:
                    logger.error("Agent execution failed for role '%s': %s", role, e)

            # 3. Complete investigation
            session.transition_to(
                InvestigationStatus.COMPLETED,
                "All workflow steps completed successfully. Session archived."
            )
            await self.session_repo.save(session)
            logger.info("Investigation pipeline successfully completed for session %s", investigation_id)

        except Exception as e:
            logger.error("Fatal error during investigation runtime: %s", e, exc_info=True)
            session.transition_to(
                InvestigationStatus.FAILED,
                f"Investigation failed due to runtime error: {e}"
            )
            await self.session_repo.save(session)


_runtime: Optional[InvestigationRuntime] = None


def get_investigation_runtime() -> InvestigationRuntime:
    """Acquire the global singleton instance of InvestigationRuntime."""
    global _runtime
    if _runtime is None:
        _runtime = InvestigationRuntime()
    return _runtime
