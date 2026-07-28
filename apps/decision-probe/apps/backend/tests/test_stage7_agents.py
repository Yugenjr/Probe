import pytest
from services.severity_agent import SeverityAgent
from services.incident_commander_agent import IncidentCommanderAgent
from services.response_planner_agent import ResponsePlannerAgent
from services.communication_agent import CommunicationAgent
from services.resolution_tracker_agent import ResolutionTrackerAgent
from services.knowledge_agent import KnowledgeAgent

@pytest.mark.asyncio
async def test_severity_agent_mock():
    agent = SeverityAgent()
    rc = {"title": "Database connection pool exhaustion"}
    metrics = {"metrics": []}
    
    res = await agent.classify_severity(rc, metrics, error_volume=120)
    assert res["severity"] == "SEV2"
    assert "failures" in res["impact_summary"]
    
    res_low = await agent.classify_severity({"title": "Minor warning"}, metrics, error_volume=10)
    assert res_low["severity"] == "SEV3"

@pytest.mark.asyncio
async def test_incident_commander_agent_mock():
    agent = IncidentCommanderAgent()
    rc = {"root_cause": {"title": "Database connection pool exhaustion", "description": "Exceeded database connections pool limit", "confidence": 0.75}}
    
    res = await agent.generate_overview(rc)
    assert "incident_title" in res
    assert res["current_status"] == "investigating"
    assert "payments-api" in res["affected_services"]

@pytest.mark.asyncio
async def test_response_planner_agent_mock():
    agent = ResponsePlannerAgent()
    overview = {"incident_title": "Database failure"}
    remediation = {"immediate_actions": ["Increase database connection limits"]}
    
    res = await agent.generate_response_plan(overview, remediation)
    assert "tasks" in res
    assert len(res["tasks"]) >= 1
    assert res["tasks"][0]["title"] == "Increase database connection limits"

@pytest.mark.asyncio
async def test_communication_agent_mock():
    agent = CommunicationAgent()
    overview = {"incident_title": "Database failure"}
    severity = {"severity": "SEV2", "impact_summary": "Payments impacted"}
    
    res = await agent.generate_updates(overview, severity)
    assert "updates" in res
    assert len(res["updates"]) >= 3
    channels = {u["channel"] for u in res["updates"]}
    assert "slack" in channels
    assert "email" in channels

@pytest.mark.asyncio
async def test_resolution_tracker_agent_mock():
    agent = ResolutionTrackerAgent()
    tasks = [{"title": "Fix pool", "status": "completed"}]
    remediation = {"immediate_actions": ["Increase limits"]}
    
    res = await agent.evaluate_resolution(tasks, remediation)
    assert res["status"] == "monitoring"
    assert "exhaustion" in res["remaining_risks"][0].lower() or "pooling" in res["remaining_risks"][0].lower()

@pytest.mark.asyncio
async def test_knowledge_agent_mock():
    agent = KnowledgeAgent()
    rc = {"root_cause": {"title": "Database connection pool exhaustion"}}
    remediation = {"permanent_fixes": ["Adaptive pooling"]}
    
    res = await agent.generate_knowledge(rc, remediation)
    assert "problem" in res
    assert "solution" in res
    assert "prevention" in res
