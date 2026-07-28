import asyncio
import json
import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel, create_engine
from storage.models import Workspace
from services.context_builder import ContextBuilder
from services.planner import Planner
from inference.client import InferenceClient
from services.patch_builder import PatchBuilder

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

async def run_demo():
    # 1. Setup in-memory SQLite and initial Workspace
    logger.info("--- 1. SETTING UP IN-MEMORY SQLITE ---")
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        ws = Workspace(title="Payment Failure Incident Analysis")
        session.add(ws)
        session.commit()
        session.refresh(ws)
        workspace_id = ws.id
        logger.info(f"Created Workspace ID: {workspace_id}")

    # 2. Load Incident JSON
    logger.info("--- 2. LOADING INCIDENT JSON ---")
    incident_path = Path(__file__).parent / "tests" / "payment_failure.json"
    with open(incident_path, "r", encoding="utf-8") as f:
        incident_data = json.load(f)
    logger.info(f"Loaded Incident: {incident_data['title']}")

    # 3. Context Builder
    logger.info("--- 3. BUILDING CONTEXT ---")
    user_prompt = "Analyze this critical payment failure incident and recommend immediate actions."
    with Session(engine) as session:
        context_builder = ContextBuilder(session)
        context = context_builder.build(workspace_id, user_prompt)
        # Manually add our incident to evidence
        context.resources.evidence.append(incident_data)

    # 4. Planner
    logger.info("--- 4. RUNNING PLANNER ---")
    planner = Planner()
    plan = planner.plan(context)
    context.planner_output = plan
    logger.info(f"Planner output: {plan.model_dump()}")

    # 5. Gemini Inference
    logger.info("--- 5. RUNNING GEMINI INFERENCE ---")
    client = InferenceClient()
    response = await client.generate(context)
    logger.info("Successfully received and parsed Structured JSON from Gemini.")
    print(json.dumps(response.model_dump(), indent=2))

    # 6. Patch Builder
    logger.info("--- 6. BUILDING PATCH & UPDATING WORKSPACE ---")
    with Session(engine) as session:
        patch_builder = PatchBuilder(session)
        # apply_operations applies the LLM response to SQLite
        patch_builder.apply_operations(workspace_id, response.operations)
        
        # 7. Verify SQLite Updates
        logger.info("--- 7. VERIFYING SQLITE UPDATES ---")
        updated_context = context_builder.build(workspace_id, "")
        logger.info(f"Blocks in Workspace: {len(updated_context.blocks)}")
        for b in updated_context.blocks:
            logger.info(f"- [{b['type']}] {str(b['content'])[:100]}...")

if __name__ == "__main__":
    asyncio.run(run_demo())
