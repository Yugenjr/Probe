import logging
import asyncio
from typing import Any, Optional, TYPE_CHECKING
from .state import InvestigationSession, InvestigationStatus
from ..domain.incident import Incident

if TYPE_CHECKING:
    from ..agents.supervisor import SupervisorCommand

logger = logging.getLogger(__name__)


class InvestigationOrchestrator:
    """Dynamic lifecycle orchestrator governing automated forensic investigations.
    
    Acts as the runtime engine that queries the SupervisorAgent for stage transitions,
    validates the transitions, and delegates to the appropriate agents.
    """
    def __init__(self, container: Optional[Any] = None):
        if container is None:
            from ..core.di import get_container
            container = get_container()
        self.container = container
        from ..agents.supervisor import SupervisorAgent
        self.supervisor = SupervisorAgent()

    async def initiate_investigation(self, incident: Incident) -> InvestigationSession:
        """Initialize runtime execution session state and advance to intake."""
        session_uuid = f"inv-{incident.incident_id}"
        session = InvestigationSession(
            session_id=session_uuid,
            investigation_id=session_uuid,
            incident=incident,
            status=InvestigationStatus.INITIALIZED,
        )
        session.transition_to(
            InvestigationStatus.INTAKE,
            f"Investigation initialized via webhook from platform: {incident.source_platform}.",
        )
        logger.info("Orchestrator initiated session %s for model %s", session.session_id, incident.model_id)
        return session

    async def execute_investigation_loop(self, session: InvestigationSession) -> InvestigationSession:
        """Execute the dynamic multi-agent scientific investigation loop commanded by the Supervisor."""
        logger.info("Starting dynamic evaluation loop for session %s", session.session_id)
        
        while session.status not in (InvestigationStatus.COMPLETED, InvestigationStatus.FAILED):
            # 1. Query Supervisor
            command: SupervisorCommand = await self.supervisor.execute(session)
            
            from .state import SupervisorDecision
            import uuid
            decision = SupervisorDecision(
                id=str(uuid.uuid4()),
                investigation_id=session.investigation_id,
                action=command.action,
                stage=command.next_stage.value if command.next_stage else "NONE",
                confidence=command.confidence,
                required_agents=command.required_agents,
                missing_information=command.missing_information,
                rationale=command.rationale,
                request_reason=command.request_reason,
            )
            session.supervisor_decisions.append(decision)

            # 2. Validate Command
            if not self._validate_command(session, command):
                logger.warning("Invalid Supervisor command rejected: %s -> %s", command.action, command.next_stage)
                session.execution_history.append(f"[Orchestrator] Rejected invalid Supervisor command: {command.action}")
                # Increment loop count as a penalty for bad commands
                session.loop_count += 1
                if session.loop_count >= session.max_loops:
                    self._escalate_and_terminate(session, "Max loops reached due to invalid Supervisor commands.")
                continue

            # 3. Handle Escalate / Terminate
            if command.action in ("ESCALATE", "TERMINATE") or command.terminate:
                status = InvestigationStatus.FAILED if command.action == "ESCALATE" else InvestigationStatus.COMPLETED
                session.transition_to(status, f"Supervisor requested termination: {command.rationale}")
                break
                
            # 4. Handle Loop Backs
            if command.action == "LOOP_BACK":
                session.loop_count += 1
                if session.loop_count >= session.max_loops:
                    self._escalate_and_terminate(session, f"Max loops ({session.max_loops}) reached during investigation.")
                    break
                session.transition_to(command.next_stage, f"Supervisor looped back: {command.rationale}")
                await asyncio.sleep(0.01)
                continue
                
            # 5. Handle Next Stage Transitions
            if command.action == "NEXT_STAGE" and command.next_stage:
                session.transition_to(command.next_stage, f"Supervisor advanced stage: {command.rationale}")
                
                if command.next_stage == InvestigationStatus.PLANNING:
                    await self._execute_planning_stage(session)
                elif command.next_stage == InvestigationStatus.EVIDENCE:
                    await self._execute_evidence_stage(session)
                elif command.next_stage == InvestigationStatus.REASONING:
                    await self._execute_reasoning_stage(session)
                elif command.next_stage == InvestigationStatus.DECISION:
                    await self._execute_decision_stage(session)
                    
                    # Memory Learn executes automatically after Decision is reached
                    from ..agents.memory import MemoryLearnAgent
                    learn_agent = MemoryLearnAgent()
                    await learn_agent.execute(session)
                else:
                    await asyncio.sleep(0.01)
                
        return session

    def _validate_command(self, session: InvestigationSession, command: 'SupervisorCommand') -> bool:
        """Strict validation of state transitions."""
        if command.terminate or command.action in ("TERMINATE", "ESCALATE"):
            return True
            
        if not command.next_stage:
            return False
            
        # Ensure we don't go to Reasoning without Evidence
        if command.next_stage == InvestigationStatus.REASONING:
            if not session.universal_evidence and not session.evidence_items:
                return False
                
        # Ensure we don't go to Decision without Hypotheses
        if command.next_stage == InvestigationStatus.DECISION:
            if not session.causal_hypothesis and not session.hypotheses:
                return False
                
        return True
    async def _execute_planning_stage(self, session: InvestigationSession):
        """Executes the planning stage, triggering proactive historical context retrieval."""
        logger.info("Executing PLANNING stage for session %s", session.session_id)
        from ..agents.memory import MemoryRecallAgent
        recall_agent = MemoryRecallAgent()
        analysis = await recall_agent.execute(session)
        session.historical_pattern_analysis = analysis

    async def _execute_evidence_stage(self, session: InvestigationSession):
        """Delegates evidence collection to the EvidenceCollector service."""
        from ..services.evidence_collector import EvidenceCollector
        collector = EvidenceCollector()
        await collector.collect(session)

    async def _execute_reasoning_stage(self, session: InvestigationSession):
        """Executes the deterministic services and cognitive agents for the Reasoning stage."""
        logger.info("Executing REASONING stage for session %s", session.session_id)
        
        from ..services.graph import EvidenceGraphBuilder
        from ..services.ranking import EvidenceRanker
        from ..agents.causal import CausalSynthesisAgent
        from ..agents.critic import AdversarialCriticAgent
        
        # 1. Build Graph
        graph_builder = EvidenceGraphBuilder()
        graph = graph_builder.build(session.evidence_bundle)
        session.evidence_graph = graph
        
        # 2. Rank Evidence
        ranker = EvidenceRanker()
        ranked_evidence = ranker.rank(session.evidence_bundle)
        
        # 3. Synthesize Causal Hypothesis
        causal_agent = CausalSynthesisAgent()
        hypothesis = await causal_agent.execute(session, ranked_evidence, graph, history=session.historical_pattern_analysis)
        session.causal_hypothesis = hypothesis
        
        # 4. Red-team Critique
        critic_agent = AdversarialCriticAgent()
        critique = await critic_agent.execute(session, hypothesis, session.evidence_bundle)
        session.critique_report = critique
        
        session.execution_history.append(f"[Orchestrator] Completed REASONING stage. Synthesized {hypothesis.hypothesis_id}, received critique verdict: {critique.overall_verdict}.")

    async def _execute_decision_stage(self, session: InvestigationSession):
        """Executes the InterventionArchitectAgent and compiles the InvestigationResult."""
        logger.info("Executing DECISION stage for session %s", session.session_id)
        
        from ..agents.architect import InterventionArchitectAgent
        from .state import InvestigationResult
        
        architect_agent = InterventionArchitectAgent()
        plan = await architect_agent.execute(session, session.causal_hypothesis, session.critique_report)
        session.remediation_plan = plan
        
        # Compile final InvestigationResult
        result = InvestigationResult(
            investigation_id=session.investigation_id,
            evidence_bundle=session.evidence_bundle,
            evidence_graph=session.evidence_graph,
            causal_hypothesis=session.causal_hypothesis,
            critique_report=session.critique_report,
            remediation_plan=session.remediation_plan
        )
        session.investigation_result = result
        
        session.execution_history.append(f"[Orchestrator] Completed DECISION stage. Compiled InvestigationResult.")

    def _escalate_and_terminate(self, session: InvestigationSession, reason: str):
        """Escalate to human and terminate the investigation FSM."""
        logger.error("Escalating session %s: %s", session.session_id, reason)
        session.transition_to(InvestigationStatus.FAILED, f"Escalated: {reason}")

