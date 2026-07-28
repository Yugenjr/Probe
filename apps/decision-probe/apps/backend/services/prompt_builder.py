import json
import os
from pathlib import Path
from .models import ReasoningContext

class PromptBuilder:
    def __init__(self):
        self.prompts_dir = Path(__file__).parent.parent / "prompts"
        
    def _load_prompt(self, filename: str) -> str:
        filepath = self.prompts_dir / filename
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def build_system_prompt(self) -> str:
        system = self._load_prompt("system.md")
        schema = self._load_prompt("workspace_patch_schema.json")
        investigation = self._load_prompt("investigation.md")
        summary = self._load_prompt("summary.md")
        decision = self._load_prompt("decision.md")
        retrieval = self._load_prompt("retrieval.md")
        
        parts = [
            system,
            "\n--- INVESTIGATION RULES ---",
            investigation,
            "\n--- SUMMARY RULES ---",
            summary,
            "\n--- DECISION RULES ---",
            decision,
            "\n--- RETRIEVAL RULES ---",
            retrieval,
            "\n--- PATCH SCHEMA ---",
            schema
        ]
        
        return "\n".join(parts)

    def build_user_prompt(self, context: ReasoningContext) -> str:
        """
        Serializes the entire context into a strictly structured string for the LLM.
        """
        prompt = [
            "--- ROLE ---",
            "You are the Lead Engineering Investigator. You autonomously reason and patch the workspace.",
            "",
            "--- MISSION ---",
            "Investigate the incident, apply your reasoning, follow the strict schemas, and output the required JSON patch.",
            "",
            "--- CURRENT WORKSPACE ---",
            f"Title: {context.workspace_title}",
            f"Description: {context.workspace_description}",
            f"Timestamp: {context.timestamp.isoformat()}",
            "",
            "--- CURRENT BLOCKS ---",
            json.dumps(context.blocks, indent=2),
            "",
            "--- CURRENT DECISIONS ---",
            json.dumps(context.current_decisions, indent=2),
            "",
            "--- CURRENT EVIDENCE ---",
            json.dumps(context.resources.evidence, indent=2),
            "",
            "--- CURRENT RESOURCES ---",
            json.dumps({"documents": context.resources.documents, "web_results": context.resources.web_results}, indent=2),
            "",
            "--- CURRENT CONVERSATION ---",
            json.dumps(context.conversation, indent=2),
            "",
            "--- USER REQUEST ---",
            context.user_prompt,
            "",
            "--- EXPECTED PATCH SCHEMA ---",
            "Output must be a JSON object with an 'operations' array, matching workspace_patch_schema.json."
        ]
        
        return "\n".join(prompt)
