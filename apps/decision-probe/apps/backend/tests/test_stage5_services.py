import pytest
from services.evidence_gap_agent import EvidenceGapAgent
from services.evidence_acquisition_agent import EvidenceAcquisitionAgent
from services.investigation_loop_agent import InvestigationLoopAgent

@pytest.mark.asyncio
async def test_evidence_gap_agent():
    agent = EvidenceGapAgent()
    root_cause = {"root_cause": {"title": "Database connection pool exhaustion", "confidence": 0.75}}
    validation = {}
    reviews = []
    timeline = {}
    
    gaps = await agent.analyze_gaps(root_cause, validation, reviews, timeline)
    assert "evidence_gaps" in gaps
    assert len(gaps["evidence_gaps"]) >= 1
    assert gaps["evidence_gaps"][0]["importance"] == "high"
    assert gaps["should_continue"] is True

@pytest.mark.asyncio
async def test_evidence_gap_agent_satisfied():
    agent = EvidenceGapAgent()
    # High confidence >= 85%
    root_cause = {"root_cause": {"title": "Database connection pool exhaustion", "confidence": 0.88}}
    gaps = await agent.analyze_gaps(root_cause, {}, [], {})
    assert len(gaps["evidence_gaps"]) == 0
    assert gaps["should_continue"] is False

@pytest.mark.asyncio
async def test_evidence_acquisition_agent():
    agent = EvidenceAcquisitionAgent()
    gaps = {
        "evidence_gaps": [
            {
                "gap": "Database connection usage metrics",
                "importance": "high",
                "required_source": "PostgreSQL Monitoring",
                "reason": "Verify connection counts"
            }
        ]
    }
    requests = await agent.generate_requests(gaps)
    assert "requests" in requests
    assert len(requests["requests"]) == 1
    assert requests["requests"][0]["type"] == "metric"
    assert "connection usage" in requests["requests"][0]["query"]

@pytest.mark.asyncio
async def test_investigation_loop_agent():
    agent = InvestigationLoopAgent()
    
    # 1. First iteration, confidence low -> waiting for evidence
    iter1 = await agent.evaluate_iteration(
        previous_iterations=[],
        current_confidence=0.75,
        should_continue=True
    )
    assert iter1["iteration"] == 1
    assert iter1["status"] == "waiting_for_evidence"
    assert iter1["confidence_change"]["before"] == 0.0
    assert iter1["confidence_change"]["after"] == 0.75

    # 2. Second iteration, confidence high -> completed
    iter2 = await agent.evaluate_iteration(
        previous_iterations=[iter1],
        current_confidence=0.88,
        should_continue=False
    )
    assert iter2["iteration"] == 2
    assert iter2["status"] == "completed"
    assert iter2["confidence_change"]["before"] == 0.75
    assert iter2["confidence_change"]["after"] == 0.88

    # 3. Third iteration limit test -> insufficient (or completed if confidence meets target)
    iter3_low = await agent.evaluate_iteration(
        previous_iterations=[iter1, {"iteration": 2, "status": "waiting_for_evidence", "confidence_change": {"before": 0.75, "after": 0.80}}],
        current_confidence=0.82,
        should_continue=True
    )
    assert iter3_low["iteration"] == 3
    assert iter3_low["status"] == "insufficient"
    assert "limit" in iter3_low["reason"]
