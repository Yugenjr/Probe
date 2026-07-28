import pytest
from services.knowledge.embedding_agent import EmbeddingAgent
from services.knowledge.incident_retrieval_agent import IncidentRetrievalAgent
from services.knowledge.similarity_agent import SimilarityAgent
from services.knowledge.learning_agent import LearningAgent
from services.knowledge.pattern_detection_agent import PatternDetectionAgent

@pytest.mark.asyncio
async def test_embedding_agent_mock():
    agent = EmbeddingAgent()
    res = await agent.embed_incident(
        incident_id="INC-1",
        title="Db Failure",
        root_cause="Exhaustion",
        services=["payments-api"]
    )
    assert res["incident_id"] == "INC-1"
    assert res["embedding_metadata"]["title"] == "Db Failure"

@pytest.mark.asyncio
async def test_incident_retrieval_agent_mock():
    agent = IncidentRetrievalAgent()
    current = {"incident_title": "Database connection pool limits"}
    res = await agent.retrieve_similar_incidents(current)
    assert "similar_incidents" in res
    assert len(res["similar_incidents"]) >= 1
    assert res["similar_incidents"][0]["incident_id"] == "INC-102"
    assert res["similar_incidents"][0]["similarity_score"] == 0.92

@pytest.mark.asyncio
async def test_similarity_agent_mock():
    agent = SimilarityAgent()
    current = {"incident_title": "Database connection saturation"}
    similar = [{"incident_id": "INC-102"}]
    
    res = await agent.compare_incidents(current, similar)
    assert "common_patterns" in res
    assert "differences" in res
    assert res["confidence_boost"] == 0.15

@pytest.mark.asyncio
async def test_learning_agent_mock():
    agent = LearningAgent()
    current = {"incident_title": "Database saturation"}
    similar = [{"incident_id": "INC-102"}]
    res = {"status": "monitoring"}
    
    out = await agent.generate_recommendations(current, similar, res)
    assert "recommendations" in out
    assert len(out["recommendations"]) >= 1
    assert out["recommendations"][0]["type"] == "investigation"

@pytest.mark.asyncio
async def test_pattern_detection_agent_mock():
    agent = PatternDetectionAgent()
    current = {"incident_title": "Database connection saturation", "affected_services": ["payments-api"]}
    similar = [{"incident_id": "INC-102"}]
    
    out = await agent.detect_patterns(current, similar)
    assert "patterns" in out
    assert len(out["patterns"]) == 1
    assert out["patterns"][0]["occurrences"] == 5
    assert "payments-api" in out["patterns"][0]["affected_services"]
