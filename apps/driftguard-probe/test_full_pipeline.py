import asyncio
import json
from probe.engine.state import InvestigationSession, InvestigationStatus
from probe.domain.incident import Incident
from probe.engine.orchestrator import InvestigationOrchestrator
from probe.domain.memory import HistoricalPatternAnalysis

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
        status=InvestigationStatus.PLANNING,
        investigation_goal="Identify root cause of drift."
    )
    
    orchestrator = InvestigationOrchestrator()
    
    print("=== Executing PLANNING stage (Memory Recall) ===")
    await orchestrator._execute_planning_stage(session)
    if session.historical_pattern_analysis:
        print(f"Memory Recall Confidence: {session.historical_pattern_analysis.retrieval_confidence}")
        print(f"Recommended Evidence: {session.historical_pattern_analysis.recommended_evidence}")
    else:
        print("No historical pattern analysis retrieved.")

    print("\n=== Executing EVIDENCE stage ===")
    await orchestrator._execute_evidence_stage(session)
    
    print("\n=== Executing REASONING stage ===")
    await orchestrator._execute_reasoning_stage(session)
    print(f"Graph Nodes: {len(session.evidence_graph.nodes)}")
    print(f"Hypothesis Root Cause: {session.causal_hypothesis.primary_root_cause}")
    print(f"Critique Verdict: {session.critique_report.overall_verdict}")
    print(f"Critique Recommendations: {session.critique_report.recommended_action}")
    
    print("\n=== Executing DECISION stage (and Memory Learn) ===")
    await orchestrator._execute_decision_stage(session)
    print(f"Remediation Short Term: {session.remediation_plan.short_term_fix}")
    print(f"Remediation Risk: {session.remediation_plan.risk_level}")
    
    print("\n=== Final InvestigationResult ===")
    if session.investigation_result:
        print(f"Result schema version: {session.investigation_result.schema_version}")
        print(f"Evidence metrics items: {len(session.investigation_result.evidence_bundle.metrics)}")
        print(f"Hypothesis ID: {session.investigation_result.causal_hypothesis.hypothesis_id}")
        print(f"Remediation ID: {session.investigation_result.remediation_plan.remediation_id}")
        print("Success! InvestigationResult and Memory properly executed.")
    else:
        print("Failed to compile InvestigationResult.")

if __name__ == "__main__":
    asyncio.run(run_test())
