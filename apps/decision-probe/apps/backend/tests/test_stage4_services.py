import pytest
from services.validation_agent import ValidationAgent
from services.remediation_agent import RemediationAgent

@pytest.mark.asyncio
async def test_validation_agent_mock():
    agent = ValidationAgent()
    root_cause = {
        "title": "Database connection pool exhaustion",
        "description": "Exceeded database max connections limit.",
        "confidence": 0.75,
        "supporting_chunks": ["chunk_2"]
    }
    timeline = {"events": []}
    graph = {"nodes": [], "edges": []}
    chunks = [{"id": "chunk_2", "snippet": "connections limit exceeded"}]

    validation = await agent.validate_root_cause(root_cause, timeline, graph, chunks)
    
    assert "validation_plan" in validation
    assert len(validation["validation_plan"]) >= 1
    assert "action" in validation["validation_plan"][0]
    assert "reason" in validation["validation_plan"][0]
    
    assert "missing_information" in validation
    assert len(validation["missing_information"]) >= 1
    
    assert "validation_summary" in validation
    assert "limit" in validation["validation_summary"]

@pytest.mark.asyncio
async def test_validation_agent_insufficient_evidence():
    agent = ValidationAgent()
    root_cause = {
        "title": "Insufficient Evidence",
        "description": "No evidence details.",
        "confidence": 0.0,
        "supporting_chunks": []
    }
    
    validation = await agent.validate_root_cause(root_cause, {}, {}, [])
    assert "validation_summary" in validation
    assert "insufficient evidence" in validation["validation_summary"].lower()

@pytest.mark.asyncio
async def test_remediation_agent_mock():
    agent = RemediationAgent()
    root_cause = {
        "title": "Database connection pool exhaustion",
        "description": "Exceeded limits.",
        "confidence": 0.75,
        "supporting_chunks": ["chunk_2"]
    }
    validation = {"validation_plan": [], "missing_information": [], "validation_summary": ""}
    chunks = [{"id": "chunk_2", "snippet": "exhausted"}]

    remediation = await agent.generate_remediation(root_cause, validation, chunks)

    assert "immediate_actions" in remediation
    assert len(remediation["immediate_actions"]) >= 1
    assert "permanent_fixes" in remediation
    assert len(remediation["permanent_fixes"]) >= 1
    assert "prevention_steps" in remediation
    assert len(remediation["prevention_steps"]) >= 1
    assert "summary" in remediation
