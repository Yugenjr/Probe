import pytest
from sqlmodel import Session, SQLModel, create_engine
from storage.models import Workspace, Block, ProviderSetting
from services.context_builder import ContextBuilder
from services.planner import LegacyPlanner as Planner
from services.prompt_builder import PromptBuilder

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_context_builder(session: Session):
    # Setup Data
    ws = Workspace(title="Test Workspace")
    session.add(ws)
    session.commit()
    
    block1 = Block(workspace_id=ws.id, type="incident", order=0, content={"text": "User says hello"})
    block2 = Block(workspace_id=ws.id, type="decision", order=1, content={"text": "Hello processed"})
    session.add_all([block1, block2])
    session.commit()
    
    # Test ContextBuilder
    builder = ContextBuilder(session)
    context = builder.build(ws.id, "Please search the web for new info")
    
    assert context.workspace_id == ws.id
    assert context.workspace_title == "Test Workspace"
    assert len(context.blocks) == 2
    assert len(context.conversation) == 1 # Only incident blocks are classified as conversation
    assert context.conversation[0]["content"]["text"] == "User says hello"

def test_planner():
    planner = Planner()
    
    # Test 1
    from services.models import ReasoningContext
    from datetime import datetime, timezone
    
    ctx = ReasoningContext(
        workspace_id="test",
        workspace_title="test",
        user_prompt="I need to search the web and summarize.",
        timestamp=datetime.now(timezone.utc)
    )
    plan = planner.plan(ctx)
    assert plan.retrieve_web is True
    assert plan.generate_summary is True
    assert plan.retrieve_workspace_history is False

def test_prompt_builder():
    builder = PromptBuilder()
    sys_prompt = builder.build_system_prompt()
    assert "PATCH SCHEMA" in sys_prompt
    assert "You are the reasoning engine" in sys_prompt
