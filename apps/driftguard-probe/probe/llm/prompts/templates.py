import os
from pydantic import BaseModel


class PromptTemplate(BaseModel):
    """Schema representing a version-controlled prompt template."""
    name: str
    version: str
    template: str


def load_prompt_template(name: str, version: str = "v1") -> PromptTemplate:
    """Load a version-controlled markdown prompt template from the local prompts directory."""
    filename = f"{name}.{version}.md"
    dir_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(dir_path, filename)
    
    if not os.path.exists(file_path):
        # Fallback to general system constants if prompt file is missing
        fallback_map = {
            "investigator": "You are an expert MLOps Investigator Agent. Telemetry: {{ context_json }}",
            "planner": "You are the Planner Agent. Context: {{ context_json }}",
            "reporter": "You are the Reporter Agent. Inputs: {{ incident_json }} {{ plan_json }} {{ evidence_json }}",
            "hypothesis": "You are the Hypothesis Agent. Context: {{ context_json }}. Plan: {{ plan_json }}. Evidence: {{ evidence_json }}",
            "evaluator": "You are the Evaluator Agent. Hypotheses: {{ hypotheses_json }}",
        }
        fallback_tpl = fallback_map.get(name, "System prompt template fallback.")
        return PromptTemplate(name=name, version=version, template=fallback_tpl)
        
    with open(file_path, "r", encoding="utf-8") as f:
        template_str = f.read().strip()
        
    return PromptTemplate(name=name, version=version, template=template_str)
