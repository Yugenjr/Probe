from sqlmodel import Session
from .context_builder import ContextBuilder
from .planner import LegacyPlanner as Planner
from .prompt_builder import PromptBuilder
from .patch_builder import PatchBuilder
from storage.models import ExecutionLog
import json

class ReasoningEngine:
    def __init__(self, session: Session, inference_client):
        self.session = session
        self.inference_client = inference_client
        self.context_builder = ContextBuilder(session)
        self.planner = Planner()
        self.prompt_builder = PromptBuilder()
        self.patch_builder = PatchBuilder(session)

    def _yield_log(self, workspace_id: str, message: str, success: bool = True):
        log = ExecutionLog(workspace_id=workspace_id, message=message, success=success)
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return f"data: {json.dumps({'type': 'execution_log', 'payload': {'id': log.id, 'message': log.message, 'success': log.success, 'timestamp': log.timestamp.isoformat()}})}\n\n"

    async def execute_and_stream(self, workspace_id: str, user_prompt: str):
        yield self._yield_log(workspace_id, "Starting investigation...")
        
        # 1. Build Context
        context = self.context_builder.build(workspace_id, user_prompt)
        
        # 2. Plan Execution (Here we might fetch more resources)
        plan = self.planner.plan(context)
        
        # 3. Build Prompt
        system_prompt = self.prompt_builder.build_system_prompt()
        final_user_prompt = self.prompt_builder.build_user_prompt(context)

        yield self._yield_log(workspace_id, "Reasoning over context...")

        try:
            # 4. Call LLM
            llm_response = await self.inference_client.generate(context)
            
            # 5. Persist and Stream Patches
            raw_json = json.dumps([op.model_dump() for op in llm_response.operations])
            
            for sse_event in self.patch_builder.apply_and_yield_patches(workspace_id, raw_json):
                yield sse_event
                
            yield self._yield_log(workspace_id, "Workspace updated successfully.")
            
        except Exception as e:
            yield self._yield_log(workspace_id, f"Inference failed: {str(e)}", success=False)

