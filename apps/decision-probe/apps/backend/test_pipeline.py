import asyncio
from storage.database import get_session
from services.reasoning_engine import ReasoningEngine
from inference.client import InferenceClient
from services.models import ReasoningContext
from services.prompt_builder import PromptBuilder
from pydantic import BaseModel
from storage.database import create_db_and_tables

class LLMResponse(BaseModel):
    pass

async def trace_pipeline():
    print("1. User prompt: Investigating network outage")
    
    # We'll just build a mock ReasoningContext directly 
    # to see what PromptBuilder and InferenceClient do
    from datetime import datetime, timezone
    context = ReasoningContext(
        workspace_id="test_ws",
        workspace_title="Test",
        workspace_description="",
        user_prompt="Investigating network outage",
        timestamp=datetime.now(timezone.utc),
        blocks=[],
        conversation=[],
        settings={},
        provider_configuration={},
        timeline=[],
        current_decisions=[]
    )
    
    print("\n2. ReasoningContext sent to Gemini:")
    print(context.model_dump_json(indent=2))
    
    prompt_builder = PromptBuilder()
    sys_prompt = prompt_builder.build_system_prompt()
    user_prompt = prompt_builder.build_user_prompt(context)
    
    print("\nSystem Prompt snippet:", sys_prompt[:200])
    print("User Prompt snippet:", user_prompt[:200])
    
    client = InferenceClient()
    
    print("\nCalling Gemini...")
    result = await client.generate(context)
    
    print("\n3/4. Parsed Pydantic response:")
    print(result.model_dump_json(indent=2))
    
if __name__ == "__main__":
    asyncio.run(trace_pipeline())
