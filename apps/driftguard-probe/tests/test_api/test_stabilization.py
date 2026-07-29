import pytest
import os
import json
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from probe.api.main import app
from probe.storage.session_repository import get_session_repository, FileSessionStore
from probe.engine.state import InvestigationSession
from probe.domain.incident import Incident, IncidentSeverity, IncidentStatus
from probe.domain.evidence import DriftEvidence
from probe.domain.hypothesis import Hypothesis
from probe.models.recommendation import Recommendation, EvaluationResult
from probe.models.report import InvestigationReport
from probe.engine.executor import AgentExecutor
from probe.agents.base import BaseAgent
from probe.engine.registry import get_agent_registry

client = TestClient(app)


class MockSlowAgent(BaseAgent):
    @property
    def role_name(self) -> str:
        return "SlowMock"

    async def execute(self, state: InvestigationSession, **kwargs) -> dict:
        # Sleep to trigger timeout
        await asyncio.sleep(5.0)
        return {"status": "delayed"}


class MockFlakyAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attempts = 0

    @property
    def role_name(self) -> str:
        return "FlakyMock"

    async def execute(self, state: InvestigationSession, **kwargs) -> dict:
        self.attempts += 1
        if self.attempts < 2:
            raise ValueError("Failure simulation")
        return {"status": "recovered"}


@pytest.mark.asyncio
async def test_session_file_persistence() -> None:
    # Setup test file repository
    temp_dir = "storage/test_sessions"
    repo = FileSessionStore(directory=temp_dir)
    
    incident = Incident(
        incident_id="inc-persist-test",
        model_id="persist-model",
        severity=IncidentSeverity.HIGH,
        trigger_type="drift_detected"
    )
    session = InvestigationSession(
        session_id="session-persist-01",
        investigation_id="session-persist-01",
        incident=incident
    )
    
    await repo.save(session)
    
    # Assert JSON file exists
    file_path = Path(temp_dir) / "session-persist-01.json"
    assert file_path.exists()
    
    # Reload and verify
    reloaded = await repo.get("session-persist-01")
    assert reloaded is not None
    assert reloaded.incident.model_id == "persist-model"
    
    # Delete and verify clean up
    await repo.delete("session-persist-01")
    assert not file_path.exists()
    
    # Clean up test directory
    try:
        Path(temp_dir).rmdir()
    except Exception:
        pass


def test_api_sub_resources() -> None:
    # Get active session repository and inject a test session
    repo = get_session_repository()
    
    incident = Incident(
        incident_id="inc-api-test",
        model_id="api-model",
        severity=IncidentSeverity.HIGH,
        trigger_type="drift_detected",
        status=IncidentStatus.OPEN
    )
    session = InvestigationSession(
        session_id="session-api-01",
        investigation_id="session-api-01",
        incident=incident
    )
    
    # Add evidence
    evidence = DriftEvidence(
        evidence_id="ev-api-01",
        source_provider="Evidently",
        retrieved_by_tool="DriftExtractor",
        summary="Drift detected on age",
        confidence_weight=0.9,
        feature_name="age",
        distance_algorithm="psi",
        observed_distance=0.18,
        alarm_threshold=0.08
    )
    session.add_universal_evidence(evidence)
    
    # Add hypothesis
    hyp = Hypothesis(
        hypothesis_id="hyp-api-01",
        title="Feature Skew",
        detailed_reasoning="Observed statistical feature distance drift.",
        supporting_evidence_ids=["ev-api-01"],
        likelihood_score=0.9,
        explanation="Observed statistical feature distance drift.",
        confidence=0.9,
        weaknesses=[]
    )
    session.add_hypothesis(hyp)
    
    # Add evaluation result
    rec = Recommendation(
        action="Rollback",
        reason="Preprocessing bug in deployed commit.",
        priority="P0",
        estimated_risk="Low",
        estimated_time="5 min"
    )
    eval_res = EvaluationResult(
        best_hypothesis=hyp,
        alternatives=[],
        recommended_actions=[rec],
        confidence=0.9
    )
    session.evaluation_result = eval_res
    
    # Add report
    report = InvestigationReport(
        report_id="rep-api-01",
        investigation_id="session-api-01",
        incident_summary=incident,
        primary_root_cause="Feature Skew",
        supporting_evidence=[],
        tested_hypotheses=[hyp],
        experiments=[],
        recommended_action=rec,
        markdown_content="# Investigation Report\n\n- Feature Skew"
    )
    session.report = report
    
    # Save session
    asyncio.run(repo.save(session))
    
    # 1. Test GET /api/v1/investigations
    response = client.get("/api/v1/investigations")
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["status"] == "success"
    # Find our test item
    summaries = res_json["data"]["items"]
    match = next((s for s in summaries if s["id"] == "session-api-01"), None)
    assert match is not None
    assert match["model"] == "api-model"
    assert match["status"] == "received"
    assert match["confidence"] == 0.9



    # 2. Test GET /api/v1/investigations/{id}/timeline
    response = client.get("/api/v1/investigations/session-api-01/timeline")
    assert response.status_code == 200
    timeline = response.json()["data"]["timeline"]
    assert len(timeline) >= 1
    assert timeline[0]["agent"] == "Webhook Ingestion"

    # 3. Test GET /api/v1/investigations/{id}/evidence
    response = client.get("/api/v1/investigations/session-api-01/evidence")
    assert response.status_code == 200
    evidence_data = response.json()["data"]["universal_evidence"]
    assert len(evidence_data) == 1
    assert evidence_data[0]["evidence_id"] == "ev-api-01"

    # 4. Test GET /api/v1/investigations/{id}/hypotheses
    response = client.get("/api/v1/investigations/session-api-01/hypotheses")
    assert response.status_code == 200
    hypotheses_data = response.json()["data"]["hypotheses"]
    assert len(hypotheses_data) == 1
    assert hypotheses_data[0]["hypothesis_id"] == "hyp-api-01"

    # 5. Test GET /api/v1/investigations/{id}/evaluation
    response = client.get("/api/v1/investigations/session-api-01/evaluation")
    assert response.status_code == 200
    eval_data = response.json()["data"]["evaluation_result"]
    assert eval_data is not None
    assert eval_data["confidence"] == 0.9

    # 6. Test GET /api/v1/investigations/{id}/report
    response = client.get("/api/v1/investigations/session-api-01/report")
    assert response.status_code == 200
    report_data = response.json()["data"]["report"]
    assert report_data is not None
    assert "Feature Skew" in report_data["markdown_content"]


@pytest.mark.asyncio
async def test_executor_timeout_and_retry() -> None:
    # Register mock agents
    registry = get_agent_registry()
    registry.register("SlowMock", MockSlowAgent)
    registry.register("FlakyMock", MockFlakyAgent)

    # Setup test repository and executor
    repo = FileSessionStore(directory="storage/test_executor_sessions")
    executor = AgentExecutor(registry=registry, session_repo=repo)
    
    incident = Incident(
        incident_id="inc-exec-test",
        model_id="exec-model",
        severity=IncidentSeverity.MEDIUM,
        trigger_type="drift_detected"
    )
    session = InvestigationSession(
        session_id="session-exec-01",
        investigation_id="session-exec-01",
        incident=incident
    )
    
    # 1. Test timeout handler
    with pytest.raises(RuntimeError) as exc_info:
        await executor.execute(
            role_name="SlowMock",
            session=session,
            max_retries=1,
            timeout_seconds=0.5
        )
    assert "timed out after 0.5s" in str(exc_info.value)
    
    # Verify failed AgentResult recorded on session
    assert len(session.agent_results) == 1
    assert session.agent_results[0].success is False
    assert "timed out" in session.agent_results[0].metadata["error"]

    # 2. Test retry logic with recovered flaky agent
    session2 = InvestigationSession(
        session_id="session-exec-02",
        investigation_id="session-exec-02",
        incident=incident
    )
    res = await executor.execute(
        role_name="FlakyMock",
        session=session2,
        max_retries=3,
        timeout_seconds=2.0
    )
    assert res.success is True
    assert res.retries == 1
    assert len(session2.agent_results) == 1
    assert session2.agent_results[0].success is True
    
    # Cleanup test session files
    await repo.delete("session-exec-01")
    await repo.delete("session-exec-02")
    try:
        Path("storage/test_executor_sessions").rmdir()
    except Exception:
        pass
