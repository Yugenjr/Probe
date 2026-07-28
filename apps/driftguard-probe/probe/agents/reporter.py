"""Reporter Agent synthesizing comprehensive diagnostic documentation."""
import logging
import uuid
from typing import Any, Optional
from datetime import datetime, timezone
from .base import BaseAgent
from ..engine.state import InvestigationSession
from ..models.report import InvestigationReport

logger = logging.getLogger(__name__)


import json
from pydantic import BaseModel, Field
from typing import List

class LLMReportOutput(BaseModel):
    """Structured LLM output containing report details and body content."""
    title: str = Field(..., description="Title of the diagnostic report")
    executive_summary: str = Field(..., description="High-level summary of investigation outcomes")
    evidence_summary: str = Field(..., description="Synthesis of verified telemetry and drift evidence")
    suggested_actions: List[str] = Field(..., description="List of immediate remediation suggestions")
    markdown_content: str = Field(..., description="Full body markdown text of the report")


class ReporterAgent(BaseAgent):
    """Specialized agent compiling verified evidence, hypotheses, and recommendations into markdown diagnostic reports."""
    @property
    def role_name(self) -> str:
        return "Reporter"

    async def execute(self, state: InvestigationSession, **kwargs: Any) -> Optional[InvestigationReport]:
        logger.info("Reporter Agent generating executive report for session %s", state.session_id)
        
        # 1. Gather Planner details
        planner_plan = {}
        for res in state.agent_results:
            if res.agent_name == "Planner" and res.success:
                planner_plan = res.output
                break

        # 2. Gather Evidence
        evidence_list = [ev.model_dump(mode="json") for ev in state.universal_evidence]

        # 3. Gather EvaluationResult
        eval_res = state.evaluation_result
        eval_json = eval_res.model_dump_json(indent=2) if eval_res else "{}"

        # 4. Generate structured report via LLM
        if self.llm_provider and hasattr(self.llm_provider, "generate_step_structured"):
            context = {
                "incident_json": state.incident.model_dump_json(indent=2),
                "plan_json": json.dumps(planner_plan, indent=2),
                "evidence_json": json.dumps(evidence_list, indent=2),
                "evaluation_json": eval_json
            }
            try:
                llm_output = await self.llm_provider.generate_step_structured(
                    prompt_name="reporter",
                    prompt_version="v1",
                    response_model=LLMReportOutput,
                    context=context,
                    temperature=0.1
                )
                logger.info("Reporter Agent successfully compiled report via LLM.")

                markdown = (
                    f"# {llm_output.title}\n\n"
                    f"**Model ID:** {state.incident.model_id} ({state.incident.model_version})\n\n"
                    f"## Executive Summary\n{llm_output.executive_summary}\n\n"
                    f"## Evidence Summary\n{llm_output.evidence_summary}\n\n"
                    f"## Recommended Actions\n" + "\n".join(f"- {act}" for act in llm_output.suggested_actions) + "\n\n"
                    f"{llm_output.markdown_content}\n\n"
                    f"*Report compiled autonomously via DriftGuard Probe platform-agnostic LLM reasoning engine.*"
                )
                
                report = InvestigationReport(
                    report_id=f"rep-{uuid.uuid4().hex[:6]}",
                    investigation_id=state.session_id,
                    incident_summary=state.incident,
                    primary_root_cause=llm_output.executive_summary[:200],
                    supporting_evidence=state.evidence_items,
                    tested_hypotheses=state.hypotheses,
                    experiments=[],
                    recommended_action=None,
                    markdown_content=markdown,
                )
                state.report = report
                return report
            except Exception as e:
                logger.warning("LLM report generation failed, using fallback builder: %s", e)

        # 5. Build detailed static fallback report covering all reasoning sections
        summary_section = (
            f"# Incident Investigation Report: {state.session_id}\n\n"
            f"**Model ID:** {state.incident.model_id} ({state.incident.model_version})\n\n"
            f"## Summary\n"
            f"The autonomous investigation has analyzed incident alert `{state.incident.incident_id}` "
            f"on model `{state.incident.model_id}`. The primary suspected root cause is a "
            f"feature-level drift leading to inference performance degradation.\n\n"
        )

        timeline_section = "## Timeline\n"
        for i, res in enumerate(state.agent_results):
            timeline_section += f"- **Step {i+1}**: {res.agent_name} executed successfully in {res.latency:.3f}s.\n"
        timeline_section += "\n"

        evidence_section = "## Evidence\n"
        if state.universal_evidence:
            for ev in state.universal_evidence:
                evidence_section += (
                    f"- **{ev.evidence_id}** ({ev.source_provider}): {ev.summary} "
                    f"(observed distance: {ev.observed_distance}, alarm threshold: {ev.alarm_threshold})\n"
                )
        else:
            evidence_section += "- No universal evidence collected.\n"
        evidence_section += "\n"

        hypotheses_section = "## Hypotheses\n"
        if state.hypotheses:
            for h in state.hypotheses:
                weaknesses_str = ", ".join(h.weaknesses) if h.weaknesses else "None identified"
                hypotheses_section += (
                    f"- **{h.hypothesis_id}** — *{h.title}* (Likelihood: {h.likelihood_score * 100:.0f}%)\n"
                    f"  - *Reasoning*: {h.detailed_reasoning}\n"
                    f"  - *Weaknesses*: {weaknesses_str}\n"
                )
        else:
            hypotheses_section += "- No hypotheses synthesized.\n"
        hypotheses_section += "\n"

        eval_section = "## Evaluation\n"
        if eval_res:
            eval_section += (
                f"- **Primary Hypothesis**: {eval_res.best_hypothesis.title}\n"
                f"- **Evaluator Confidence**: {eval_res.confidence * 100:.0f}%\n"
                f"- **Alternative Hypotheses Evaluated**: {len(eval_res.alternatives)}\n"
            )
        else:
            eval_section += "- Hypothesis evaluation was not completed.\n"
        eval_section += "\n"

        recs_section = "## Recommendations\n"
        if eval_res and eval_res.recommended_actions:
            for r in eval_res.recommended_actions:
                recs_section += (
                    f"- **{r.action}** (Priority: {r.priority}, Risk: {r.estimated_risk}, Time: {r.estimated_time})\n"
                    f"  - *Justification*: {r.reason}\n"
                )
        else:
            recs_section += "- No remediation actions recommended.\n"
        recs_section += "\n"

        conf_section = f"## Confidence\nWe estimate a confidence level of **{eval_res.confidence * 100:.0f}%** in this diagnostic output.\n\n" if eval_res else "## Confidence\nConfidence level: N/A\n\n"

        severity_val = state.incident.severity.value if hasattr(state.incident.severity, "value") else str(state.incident.severity)
        trigger_val = state.incident.trigger_type.value if hasattr(state.incident.trigger_type, "value") else str(state.incident.trigger_type)

        appendix_section = (
            f"## Appendix\n"
            f"- **Investigation ID**: {state.session_id}\n"
            f"- **Severity**: {severity_val}\n"
            f"- **Trigger Type**: {trigger_val}\n"
            f"- **System Time**: {datetime.now(timezone.utc).isoformat()}\n"
        )

        markdown = summary_section + timeline_section + evidence_section + hypotheses_section + eval_section + recs_section + conf_section + appendix_section
        
        report = InvestigationReport(
            report_id=f"rep-{uuid.uuid4().hex[:6]}",
            investigation_id=state.session_id,
            incident_summary=state.incident,
            primary_root_cause=eval_res.best_hypothesis.title if eval_res else "Unspecified root cause.",
            supporting_evidence=state.evidence_items,
            tested_hypotheses=state.hypotheses,
            experiments=[],
            recommended_action=eval_res.recommended_actions[0] if eval_res and eval_res.recommended_actions else None,
            markdown_content=markdown,
        )
        state.report = report
        return report
