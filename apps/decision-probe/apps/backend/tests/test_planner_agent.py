import pytest
from services.planner import Planner

@pytest.mark.asyncio
async def test_planner_strategy_mock_plan():
    planner = Planner()
    
    goal = "Investigate high memory usage and container restarts on service billing"
    chunks = [
        {"title": "logs.txt", "snippet": "Out of memory error, container killed", "source": "document"}
    ]
    
    plan = await planner.plan(goal, "Workspace Memory Issue", chunks)
    
    # Verify the structure matches our required schema
    assert isinstance(plan, dict)
    assert "objectives" in plan
    assert "questions" in plan
    assert "evidence_needed" in plan
    assert "priority" in plan
    
    assert plan["priority"] == "high"  # due to 'outage', 'failure', 'restarts', etc.
    assert len(plan["objectives"]) > 0
    assert len(plan["questions"]) > 0
    assert len(plan["evidence_needed"]) > 0

def test_planner_json_parsing():
    planner = Planner()
    raw_response = """
    ```json
    {
      "objectives": ["Identify memory leak components"],
      "questions": ["Is memory leak caused by cache?"],
      "evidence_needed": ["Heap dump profile"],
      "priority": "high"
    }
    ```
    """
    plan = planner._parse_json(raw_response)
    assert plan["objectives"] == ["Identify memory leak components"]
    assert plan["priority"] == "high"
