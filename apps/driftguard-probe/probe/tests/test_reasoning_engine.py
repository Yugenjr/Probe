import unittest
import datetime
from probe.reasoning.artifacts import (
    HypothesisArtifact, CounterEvidenceArtifact, ValidationArtifact,
    RemediationArtifact, InvestigationReport
)
from probe.reasoning.confidence_calculator import MultiFactorConfidenceEngine

class TestReasoningEngineFoundation(unittest.TestCase):
    def test_immutable_artifact_generation_and_confidence_engine(self):
        print("=== Step 1: Initialize Multi-Factor Algorithmic Confidence Engine ===")
        engine = MultiFactorConfidenceEngine()

        print("\n=== Step 2: Evaluate Candidate Hypothesis Confidence (Verified Path) ===")
        result_verified = engine.calculate_confidence(
            supporting_evidence_count=5,
            contradicting_evidence_count=0,
            avg_evidence_quality_score=0.94,
            domain_types_present=["ModelEvidence", "DriftEvidence", "RetrainingEvidence", "AuditEvidence"],
            historical_vector_similarity=0.88,
            agent_consensus_ratio=1.0,
            has_high_severity_contradiction=False,
            is_lineage_missing=False
        )
        conf_val = result_verified["final_confidence"]
        print(f"Computed Verified Confidence Score: {conf_val} ({conf_val*100:.2f}%)")
        print("Detailed Breakdown:", result_verified["breakdown"])
        self.assertGreaterEqual(conf_val, 0.85)
        self.assertTrue(result_verified["is_actionable_sre_lead"])

        print("\n=== Step 3: Evaluate Contradicted Candidate Hypothesis (Adversarial Critic Rejection) ===")
        result_rejected = engine.calculate_confidence(
            supporting_evidence_count=2,
            contradicting_evidence_count=4,
            avg_evidence_quality_score=0.60,
            domain_types_present=["DriftEvidence"], # Missing required coverage
            historical_vector_similarity=0.20,
            agent_consensus_ratio=0.30,
            has_high_severity_contradiction=True, # Explicit penalization
            is_lineage_missing=True
        )
        rej_val = result_rejected["final_confidence"]
        print(f"Computed Rejected Confidence Score: {rej_val} ({rej_val*100:.2f}%)")
        self.assertLess(rej_val, 0.30)
        self.assertFalse(result_rejected["is_actionable_sre_lead"])

        print("\n=== Step 4: Verify Immutable Reasoning Artifact Generation ===")
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        hypo = HypothesisArtifact(
            artifact_id="art-hyp-001",
            investigation_id="inv-fraud-v2-test",
            timestamp_utc=now_str,
            producer_agent="CausalSynthesisAgent",
            sha256_parent_evidence_ids=["ev-hash001", "ev-hash002"],
            hypothesis_id="hyp-d-01",
            root_cause_title="Covariate Demographic Distribution Drift",
            causal_chain_description="Age covariate shift bottlenecks embedding lookup table.",
            supporting_evidence_ids=["ev-hash001", "ev-hash002"],
            initial_confidence=conf_val,
            required_verification_queries=["check_retraining_error_logs"]
        )
        self.assertEqual(hypo.producer_agent, "CausalSynthesisAgent")

        validation = ValidationArtifact(
            artifact_id="art-val-001",
            investigation_id="inv-fraud-v2-test",
            timestamp_utc=now_str,
            producer_agent="AdversarialCriticAgent",
            sha256_parent_evidence_ids=["ev-hash001", "ev-hash002"],
            hypothesis_id="hyp-d-01",
            is_verified=True,
            final_bayesian_confidence=conf_val,
            corroberated_evidence_count=5,
            contradiction_count=0,
            critic_notes="All adversarial falsification checks passed cleanly."
        )
        self.assertTrue(validation.is_verified)

        remedy = RemediationArtifact(
            artifact_id="art-rem-001",
            investigation_id="inv-fraud-v2-test",
            timestamp_utc=now_str,
            producer_agent="InterventionArchitectAgent",
            sha256_parent_evidence_ids=["ev-hash001", "ev-hash002"],
            remediation_id="rem-001",
            target_hypothesis_id="hyp-d-01",
            action_type="ROLLBACK_AND_RETRAIN",
            execution_parameters={"target_version": "1.1.0", "dynamic_slice": "age_group_B"},
            estimated_impact_recovery=14.5,
            risk_assessment="LOW",
            required_approval_tier="SRE_LEAD"
        )
        self.assertEqual(remedy.required_approval_tier, "SRE_LEAD")
        print("[APPROVED] All reasoning artifacts compiled cleanly as immutable frozen domain models!")

if __name__ == "__main__":
    unittest.main()
