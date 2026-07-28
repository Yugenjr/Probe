from typing import List, Dict, Any, Optional

class MultiFactorConfidenceEngine:
    """
    Production algorithmic confidence engine for Probe.
    Replaces arbitrary generative LLM probability hallucinations with a deterministic
    7-Factor Weighted Composite evaluation model.
    """
    def __init__(
        self,
        weight_quality: float = 0.25,
        weight_consistency: float = 0.20,
        weight_coverage: float = 0.15,
        weight_similarity: float = 0.15,
        weight_consensus: float = 0.15,
        penalty_contradiction: float = 0.30,
        penalty_missing_lineage: float = 0.10
    ):
        self.w_q = weight_quality
        self.w_c = weight_consistency
        self.w_v = weight_coverage
        self.w_s = weight_similarity
        self.w_a = weight_consensus
        self.p_contra = penalty_contradiction
        self.p_missing = penalty_missing_lineage

    def calculate_confidence(
        self,
        supporting_evidence_count: int,
        contradicting_evidence_count: int,
        avg_evidence_quality_score: float,
        domain_types_present: List[str],
        historical_vector_similarity: float,
        agent_consensus_ratio: float,
        has_high_severity_contradiction: bool = False,
        is_lineage_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Computes bounded final confidence between 0.00 and 1.00 and returns auditable formula breakdown.
        """
        # 1. Evidence Quality ($F_1$)
        f1_quality = max(0.0, min(1.0, float(avg_evidence_quality_score)))

        # 2. Evidence Consistency ($F_2$)
        total_items = supporting_evidence_count + contradicting_evidence_count
        f2_consistency = float(supporting_evidence_count) / max(1, total_items)

        # 3. Evidence Coverage ($F_3$) - Requirement of 4 foundational pillars
        required_domains = {"ModelEvidence", "DriftEvidence", "RetrainingEvidence", "AuditEvidence"}
        present_set = set(domain_types_present)
        f3_coverage = len(present_set.intersection(required_domains)) / 4.0

        # 4. Historical Similarity ($F_4$)
        f4_similarity = max(0.0, min(1.0, float(historical_vector_similarity)))

        # 5. Agent Consensus ($F_5$)
        f5_consensus = max(0.0, min(1.0, float(agent_consensus_ratio)))

        # Weighted baseline sum
        baseline_score = (
            (self.w_q * f1_quality) +
            (self.w_c * f2_consistency) +
            (self.w_v * f3_coverage) +
            (self.w_s * f4_similarity) +
            (self.w_a * f5_consensus)
        )

        # Apply algorithmic deductions
        deductions = 0.0
        if has_high_severity_contradiction:
            deductions += self.p_contra
        if is_lineage_missing:
            deductions += self.p_missing

        raw_final = baseline_score - deductions
        final_confidence = round(max(0.0, min(1.0, raw_final)), 4)

        return {
            "final_confidence": final_confidence,
            "is_actionable_auto": final_confidence >= 0.90,
            "is_actionable_sre_lead": final_confidence >= 0.75,
            "breakdown": {
                "quality_factor_score": round(f1_quality * self.w_q, 4),
                "consistency_factor_score": round(f2_consistency * self.w_c, 4),
                "coverage_factor_score": round(f3_coverage * self.w_v, 4),
                "similarity_factor_score": round(f4_similarity * self.w_s, 4),
                "consensus_factor_score": round(f5_consensus * self.w_a, 4),
                "deductions_applied": round(deductions, 4)
            }
        }
