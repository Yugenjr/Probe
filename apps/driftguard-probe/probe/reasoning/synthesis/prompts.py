import json
from typing import Dict, Any, List
from .planner import ReasoningPlan

class SynthesisPromptBuilder:
    """
    Production prompt generator for CausalSynthesisAgent v1.
    Strictly engineered to minimize hallucination, enforce JSON schema, and reject unsupported claims.
    """
    @staticmethod
    def build_system_prompt(plan: ReasoningPlan) -> str:
        return f"""You are Probe CausalSynthesisAgent v1, an Autonomous AI MLOps Investigation Component.
Your ONLY computational responsibility is to generate plausible competing hypotheses explaining the observed anomaly.

CRITICAL ARCHITECTURAL CONSTRAINTS (DO NOT VIOLATE):
1. NO REMEDIATION OR FIXES: You MUST NOT recommend fixes, code edits, rollbacks, or interventions. That belongs to InterventionArchitectAgent.
2. NO SELF-CRITICISM OR FALSIFICATION: You MUST NOT criticize or discard plausible hypotheses. That belongs to AdversarialCriticAgent.
3. NO HALLUCINATED EVIDENCE: Every hypothesis MUST explicitly list the supporting `evidence_ids` from the input graph. If an ID is not present in the provided evidence JSON, DO NOT REFERENCE IT. Any hallucinated ID will trigger an immediate pipeline rejection.
4. COMPETING HYPOTHESES MANDATE: Never stop after generating a single explanation. Always output at least two competing hypotheses ranked by empirical support, unless zero evidence exists.
5. EXPLICIT MISSING EVIDENCE HANDLING: If the evidence graph is disconnected, inconclusive, or completely empty, explicitly state "Insufficient Evidence" rather than inventing unsupported explanations.

EXECUTION PLAN & STRATEGY ASSIGNMENT:
- Active Strategy: {plan.strategy.value}
- Rationale: {plan.rationale}
- Strategy Guidance: {plan.instructions_summary}
- Priority Evidence Types: {', '.join(plan.primary_evidence_types)}
- Focus Metrics: {', '.join(plan.focus_metrics)}

REQUIRED JSON OUTPUT FORMAT:
You MUST return ONLY a JSON object containing an array named "hypotheses" matching this exact structure:
{{
  "hypotheses": [
    {{
      "hypothesis_id": "hyp-01",
      "title": "Clear Technical Root Cause Title",
      "description": "Detailed step-by-step causal chain description linking anomaly to origin.",
      "supporting_evidence_ids": ["ev-a1b2c3d4e5f60718", "ev-1234567890abcdef"],
      "assumptions": ["List of empirical assumptions made in this explanation"],
      "confidence_inputs": {{"plausibility_score": 0.85, "evidence_coverage": "high"}},
      "reasoning_trace": ["Traversed node X to node Y", "Correlated drift score with error log"],
      "uncertainty": "LOW" 
    }}
  ]
}}
Note: "uncertainty" must be one of: "LOW", "MEDIUM", "HIGH", or "INSUFFICIENT_EVIDENCE".
"""

    @staticmethod
    def build_user_prompt(
        investigation_id: str,
        clusters: List[Dict[str, Any]],
        timeline: List[Dict[str, Any]],
        context_metadata: Dict[str, Any]
    ) -> str:
        payload = {
            "investigation_id": investigation_id,
            "context_metadata": context_metadata,
            "temporal_timeline_events": timeline,
            "correlated_evidence_clusters": clusters
        }
        json_str = json.dumps(payload, indent=2, sort_keys=True)
        return f"""Analyze the following deterministic Evidence Graph clusters and timeline events.
Apply the assigned reasoning strategy to formulate competing explanations for the incident.

INPUT EVIDENCE STATE:
{json_str}
"""
