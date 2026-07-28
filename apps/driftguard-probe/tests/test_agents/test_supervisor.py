"""Unit tests verifying supervisor agent routing and state progression."""
import asyncio
import pytest
from probe.core.supervisor import CoreSupervisor
from probe.agents.supervisor import SupervisorAgent
from probe.models.incident import Incident, IncidentSeverity
from probe.core.lifecycle import InvestigationStatus


def test_supervisor_initializes_and_completes_investigation():
    """Verify core supervisor initializes state and supervisor agent executes full workflow progression."""
    incident = Incident(
        incident_id="inc-test-unit",
        model_id="fraud_model_v1",
        model_version="1.0.0",
        trigger_type="drift_detected",
        severity=IncidentSeverity.MEDIUM,
    )
    core_super = CoreSupervisor()
    state = asyncio.run(core_super.initiate_investigation(incident))

    assert state.investigation_id == f"inv-{incident.incident_id}"
    assert state.status == InvestigationStatus.COLLECTING_EVIDENCE
    assert len(state.execution_history) == 1

    # Execute supervisor agent to get ExecutionPlan
    agent = SupervisorAgent()
    plan = asyncio.run(agent.execute(state))

    assert plan is not None
    assert len(plan.steps) == 5
    assert plan.steps[0].agent_role == "Planner"
    assert plan.steps[1].agent_role == "Investigator"
    assert plan.steps[2].agent_role == "Hypothesis"
    assert plan.steps[3].agent_role == "Evaluator"
    assert plan.steps[4].agent_role == "Reporter"
