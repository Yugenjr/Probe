import pytest
from datetime import datetime, timezone
from probe.engine.state import InvestigationSession
from probe.domain.incident import Incident, IncidentSeverity, IncidentStatus
from probe.domain.hypothesis import Hypothesis
from probe.agents.evaluator import EvaluatorAgent
from probe.models.recommendation import RecommendationAction
from probe.domain.remediation import InterventionType

@pytest.mark.asyncio
async def test_evaluator_agent_execution_with_fallback() -> None:
    # Setup test state
    incident = Incident(
        incident_id="inc-test-eval",
        model_id="demo-model",
        severity=IncidentSeverity.HIGH,
        trigger_type="drift_detected",
        status=IncidentStatus.OPEN
    )
    session = InvestigationSession(
        session_id="session-eval",
        investigation_id="session-eval",
        incident=incident
    )
    
    # Add dummy hypothesis
    hyp = Hypothesis(
        hypothesis_id="hyp-test-01",
        title="Training-serving skew",
        detailed_reasoning="Preprocessing change altered feature scaling.",
        supporting_evidence_ids=["ev-01"],
        likelihood_score=0.91,
        explanation="Preprocessing change altered feature scaling.",
        confidence=0.91,
        weaknesses=[]
    )
    session.add_hypothesis(hyp)

    # Execute EvaluatorAgent
    agent = EvaluatorAgent(llm_provider=None)
    result = await agent.execute(session)

    assert session.evaluation_result is not None
    assert session.evaluation_result.confidence == 0.91
    assert len(session.evaluation_result.recommended_actions) == 1
    assert session.evaluation_result.recommended_actions[0].action == "Rollback"
    
    # Verify legacy RemediationPlan was attached
    assert session.remediation_plan is not None
    assert session.remediation_plan.intervention_type == InterventionType.CANARY_ROLLBACK
    assert "Rollback" in session.remediation_plan.summary
