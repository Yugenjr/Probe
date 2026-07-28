import json
from typing import Type, Any, Dict, List
from pydantic import BaseModel
from probe.context.models import InvestigationContext
from probe.storage.repository import EvidenceRepository
from probe.reasoning.synthesis.planner import ReasoningPlan

class InferencePromptBuilder:
    """
    Decouples prompt construction completely from inference execution.
    Injects InvestigationContext, Evidence, ReasoningPlan, operational instructions,
    and target Pydantic JSON Schema into a finished prompt envelope.
    """
    @staticmethod
    def build_prompt(
        plan: ReasoningPlan,
        context: InvestigationContext,
        repository: EvidenceRepository,
        target_schema: Type[BaseModel],
        domain_instructions: str
    ) -> Dict[str, str]:
        # 1. Gather relevant evidence nodes
        items = repository.get_by_investigation(context.investigation_id)
        evidence_summaries = []
        for ev in items:
            evidence_summaries.append({
                "evidence_id": ev.id,
                "type": ev.type,
                "source": ev.source,
                "timestamp": ev.timestamp,
                "payload": ev.payload,
                "confidence": ev.confidence
            })

        # 2. Extract JSON schema of target artifact
        try:
            schema_json = target_schema.model_json_schema()
        except AttributeError:
            schema_json = target_schema.schema()

        system_instructions = f"""You are Probe Autonomous Inference Backend operating in structural JSON mode.
YOUR COMPUTATIONAL INSTRUCTIONS:
{domain_instructions}

MANDATORY ARCHITECTURAL & GROUNDING RULES:
1. STRUCTURED OUTPUT ONLY: You must respond directly with valid JSON matching exactly the target schema below.
2. ZERO HALLUCINATED REFERENCES: When populating supporting evidence IDs, you must reference exclusively the `evidence_id` strings provided in the input payload. Inventing an ID triggers immediate infrastructure rejection.
3. NO NATURAL LANGUAGE FLUFF: Do not output conversational preamble or markdown explanations outside the JSON schema.

TARGET OUTPUT PYDANTIC JSON SCHEMA:
{json.dumps(schema_json, indent=2)}
"""

        user_payload = {
            "investigation_id": context.investigation_id,
            "reasoning_plan_strategy": plan.strategy.value,
            "reasoning_plan_rationale": plan.rationale,
            "focus_metrics": plan.focus_metrics,
            "evidence_repository_items": evidence_summaries
        }
        user_payload_str = json.dumps(user_payload, indent=2, sort_keys=True)

        return {
            "system_instructions": system_instructions,
            "user_payload": user_payload_str,
            "target_schema_json": schema_json
        }
