import asyncio
from services.models import ReasoningContext
from inference.client import InferenceClient
from datetime import datetime, timezone
import os

async def run_demo():
    # Make sure env is loaded
    print("Initializing InferenceClient...")
    client = InferenceClient()
    
    print("\nCreating Sample ReasoningContext...")
    context = ReasoningContext(
        workspace_id="demo_ws",
        workspace_title="System Outage Investigation",
        user_prompt="I am getting reports of a 502 Bad Gateway error on the frontend. Can you summarize what we should do?",
        timestamp=datetime.now(timezone.utc),
        blocks=[
            {
                "id": "b1",
                "type": "incident",
                "order": 0,
                "content": {"text": "Frontend reporting 502 Bad Gateway"}
            }
        ]
    )
    
    print("\nCalling Gemini...")
    result = await client.generate(context)
    
    print("\nSuccess! Parsed Structured Output:")
    print(result.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(run_demo())
