import pytest
import os
from services.hypothesis_agent import HypothesisAgent
from services.critic_agent import CriticAgent
from services.decision_agent import DecisionAgent

@pytest.mark.asyncio
async def test_hypothesis_agent_mock():
    agent = HypothesisAgent()
    timeline = {
        "events": [
            {
                "timestamp": "2026-07-24T10:41:00Z",
                "type": "error",
                "service": "payments",
                "description": "PostgreSQL exceeded connection limit",
                "source_chunk": "chunk_2"
            }
        ]
    }
    chunks = [{"id": "chunk_2", "snippet": "PostgreSQL limits exceeded"}]
    
    result = await agent.generate_hypotheses({}, timeline, {}, {}, chunks)
    hypotheses = result.get("hypotheses", [])
    
    # Needs to be between 2 and 5 hypotheses
    assert len(hypotheses) >= 2
    assert len(hypotheses) <= 5
    
    # Grounding check
    assert hypotheses[0]["supporting_evidence"] == ["chunk_2"]
    assert "payments" in hypotheses[0]["description"]

@pytest.mark.asyncio
async def test_critic_agent_mock():
    agent = CriticAgent()
    hypotheses = [
        {
            "id": "hyp_1",
            "title": "Database connection pool exhaustion",
            "description": "Database pool size exceeded limits",
            "supporting_evidence": ["chunk_2"],
            "confidence": 0.80,
            "assumptions": []
        }
    ]
    timeline = {"events": []}
    
    result = await agent.review_hypotheses(hypotheses, timeline, [])
    reviews = result.get("reviews", [])
    
    assert len(reviews) == 1
    assert reviews[0]["hypothesis_id"] == "hyp_1"
    assert len(reviews[0]["strengths"]) > 0
    assert reviews[0]["confidence_adjustment"] == -0.05

@pytest.mark.asyncio
async def test_decision_agent_mock():
    agent = DecisionAgent()
    hypotheses = [
        {
            "id": "hyp_1",
            "title": "Database connection pool exhaustion",
            "description": "Exceeded database pool configuration limits.",
            "supporting_evidence": ["chunk_2"],
            "confidence": 0.80,
            "assumptions": []
        },
        {
            "id": "hyp_2",
            "title": "Broken deployment configuration update",
            "description": "Configuration parameter mismatch.",
            "supporting_evidence": ["chunk_3"],
            "confidence": 0.50,
            "assumptions": []
        }
    ]
    reviews = [
        {
            "hypothesis_id": "hyp_1",
            "strengths": ["Strongly supported"],
            "weaknesses": ["Assumes high traffic"],
            "missing_information": [],
            "confidence_adjustment": -0.05
        },
        {
            "hypothesis_id": "hyp_2",
            "strengths": ["Chronologically matched"],
            "weaknesses": ["No auth errors"],
            "missing_information": [],
            "confidence_adjustment": -0.15
        }
    ]
    
    decision = await agent.decide_root_cause(hypotheses, reviews, [])
    
    # Verify rankings (hyp_1 has adjusted 0.75, hyp_2 has 0.35)
    root_cause = decision.get("root_cause", {})
    assert root_cause["title"] == "Database connection pool exhaustion"
    assert root_cause["confidence"] == 0.75
    assert root_cause["supporting_chunks"] == ["chunk_2"]
    
    # Verify alternatives are preserved
    alts = decision.get("alternatives", [])
    assert len(alts) == 1
    assert alts[0]["title"] == "Broken deployment configuration update"
    assert alts[0]["confidence"] == 0.35

@pytest.mark.asyncio
async def test_decision_agent_insufficient_evidence():
    agent = DecisionAgent()
    
    # Hypotheses with low initial confidence
    hypotheses = [
        {
            "id": "hyp_1",
            "title": "Database connection pool exhaustion",
            "description": "Exceeded pool.",
            "supporting_evidence": ["chunk_2"],
            "confidence": 0.40,
            "assumptions": []
        }
    ]
    # Adjustments push score below 0.40
    reviews = [
        {
            "hypothesis_id": "hyp_1",
            "strengths": [],
            "weaknesses": ["Very weak"],
            "missing_information": [],
            "confidence_adjustment": -0.15
        }
    ]
    
    decision = await agent.decide_root_cause(hypotheses, reviews, [])
    
    root_cause = decision.get("root_cause", {})
    assert root_cause["title"] == "Insufficient Evidence"
    assert "insufficient evidence" in root_cause["description"].lower()
    assert root_cause["confidence"] == 0.0
