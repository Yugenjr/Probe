from .models import ReasoningContext, ExecutionPlan

class Planner:
    def plan(self, context: ReasoningContext) -> ExecutionPlan:
        """
        A deterministic heuristic engine that analyzes the user's prompt 
        and workspace state to determine what additional data needs to be retrieved.
        """
        prompt = context.user_prompt.lower()
        plan = ExecutionPlan()

        # Simple deterministic heuristics (No LLM required here)
        if "search" in prompt or "web" in prompt or "online" in prompt:
            plan.retrieve_web = True

        if "doc" in prompt or "manual" in prompt or "api" in prompt:
            plan.retrieve_documents = True
            
        if "history" in prompt or "previous" in prompt or "before" in prompt:
            plan.retrieve_workspace_history = True
            
        if "summarize" in prompt or "tldr" in prompt:
            plan.generate_summary = True

        return plan
