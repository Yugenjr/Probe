import pytest
from datetime import datetime, timezone
from probe.engine.state import InvestigationSession
from probe.domain.incident import Incident, IncidentSeverity, IncidentStatus
from probe.domain.evidence import DriftEvidence
from probe.agents.hypothesis import HypothesisAgent

class MockLLMProvider:
    pass

@pytest.mark.asyncio
async def test_hypothesis_agent_execution_with_fallback() -> None:
    # Setup test state
    incident = Incident(
        incident_id="inc-test-hyp",
        model_id="demo-model",
        severity=IncidentSeverity.HIGH,
        trigger_type="drift_detected",
        status=IncidentStatus.OPEN
    )
    session = InvestigationSession(
        session_id="session-hyp",
        investigation_id="session-hyp",
        incident=incident
    )
    
    # Add dummy evidence
    evidence = DriftEvidence(
        evidence_id="ev-01",
        source_provider="Evidently",
        retrieved_by_tool="DriftExtractor",
        summary="Drift detected on demographic age column",
        confidence_weight=0.95,
        feature_name="user_age",
        distance_algorithm="psi",
        observed_distance=0.25,
        alarm_threshold=0.1
    )
    session.add_universal_evidence(evidence)

    # Execute HypothesisAgent
    agent = HypothesisAgent(llm_provider=None)
    result = await agent.execute(session)

    assert result["status"] == "HYPOTHESIS_FORMULATED"
    assert len(session.hypotheses) == 1
    assert session.hypotheses[0].confidence == 0.92
    assert "Covariate Shift" in session.hypotheses[0].title
