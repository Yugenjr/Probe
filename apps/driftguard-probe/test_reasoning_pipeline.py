import asyncio
import json
from probe.engine.state import InvestigationSession, InvestigationStatus
from probe.domain.incident import Incident
from probe.engine.orchestrator import InvestigationOrchestrator

async def run_test():
    incident = Incident(
        incident_id="test-123",
        model_id="test-model",
        trigger_type="drift",
        severity="HIGH",
        source_platform="DriftGuard"
    )
    
    session = InvestigationSession(
        session_id="inv-test-123",
        investigation_id="inv-test-123",
        incident=incident,
        status=InvestigationStatus.EVIDENCE
    )
    
    orchestrator = InvestigationOrchestrator()
    print("=== Executing EVIDENCE stage ===")
    await orchestrator._execute_evidence_stage(session)
    
    print("\n=== Executing REASONING stage ===")
    await orchestrator._execute_reasoning_stage(session)
    print(f"Graph Nodes: {len(session.evidence_graph.nodes)}")
    print(f"Hypothesis Root Cause: {session.causal_hypothesis.primary_root_cause}")
    print(f"Critique Verdict: {session.critique_report.overall_verdict}")
    print(f"Critique Recommendations: {session.critique_report.recommended_action}")
    
    print("\n=== Executing DECISION stage ===")
    await orchestrator._execute_decision_stage(session)
    print(f"Remediation Short Term: {session.remediation_plan.short_term_fix}")
    print(f"Remediation Risk: {session.remediation_plan.risk_level}")
    
    print("\n=== Final InvestigationResult ===")
    if session.investigation_result:
        print(f"Evidence items: {len(session.investigation_result.evidence_bundle.metrics) + len(session.investigation_result.evidence_bundle.logs) + len(session.investigation_result.evidence_bundle.repo) + len(session.investigation_result.evidence_bundle.research)}")
        print(f"Hypothesis ID: {session.investigation_result.causal_hypothesis.hypothesis_id}")
        print(f"Remediation ID: {session.investigation_result.remediation_plan.remediation_id}")
        print("Success! InvestigationResult compiled perfectly.")
    else:
        print("Error: InvestigationResult is None")

if __name__ == "__main__":
    asyncio.run(run_test())
