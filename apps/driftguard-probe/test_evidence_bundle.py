import asyncio
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
    print("Executing EVIDENCE stage...")
    await orchestrator._execute_evidence_stage(session)
    
    print("\n=== Universal Evidence ===")
    print(f"Count: {len(session.universal_evidence)}")
    for ev in session.universal_evidence:
        print(f"- [{ev.evidence_type}] {ev.summary}")
        
    print("\n=== Evidence Bundle ===")
    if session.evidence_bundle:
        print(f"Metrics: {len(session.evidence_bundle.metrics)}")
        print(f"Logs: {len(session.evidence_bundle.logs)}")
        print(f"Repo: {len(session.evidence_bundle.repo)}")
        print(f"Research: {len(session.evidence_bundle.research)}")
        
        print("\n=== Timeline ===")
        print(f"Probable Trigger: {session.evidence_bundle.timeline.probable_trigger}")
        print(f"Causal Chain: {session.evidence_bundle.timeline.causal_chain}")
        print(f"Confidence: {session.evidence_bundle.timeline.confidence}")
        
        print("\n=== Summary ===")
        print(f"Total metrics: {session.evidence_bundle.summary.metric_count}")
        print(f"Coverage Score: {session.evidence_bundle.summary.coverage_score}")
        
        print("\n=== Execution Metadata ===")
        print(f"Status: {session.evidence_bundle.status}")
        print(f"Total Duration: {session.evidence_bundle.total_duration:.2f}s")
        print(f"Successful Agents: {session.evidence_bundle.successful_agents}")
        print(f"Failed Agents: {session.evidence_bundle.failed_agents}")
    else:
        print("Error: EvidenceBundle is None")

if __name__ == "__main__":
    asyncio.run(run_test())
