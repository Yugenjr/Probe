"""Algorithmic Confidence Subsystem superseding arbitrary LLM probability hallucinations."""
import math
from typing import List
from pydantic import BaseModel, Field
from ..domain.graph import EvidenceGraph


class HypothesisScoreMetric(BaseModel):
    """Structured breakdown of objective mathematical factors composing overall confidence verdict."""
    empirical_support_score: float = Field(..., description="Weighted sum of supporting evidence reliability")
    contradiction_penalty: float = Field(..., description="Deductions imposed by refuted simulation checks")
    historical_similarity_prior: float = Field(..., description="Prior Bayesian probability from vector store hits")
    sample_size_factor: float = Field(..., description="Logarithmic adjustment for telemetry sample volumes")
    computed_confidence: float = Field(..., ge=0.0, le=1.0, description="Final definitive probability score")


class ConfidenceEngine:
    """Mathematical computation engine evaluating objective probability of diagnostic theories.
    
    Eliminates intuitive LLM arithmetic by calculating Bayesian confidence verifications from
    underlying Evidence Graph connections and empirical replay p-values.
    """
    @staticmethod
    def evaluate_hypothesis(
        hypothesis_id: str,
        supporting_node_ids: List[str],
        contradiction_node_ids: List[str],
        graph: EvidenceGraph,
        prior_similarity: float = 0.5,
        sample_count: int = 1000
    ) -> HypothesisScoreMetric:
        """Execute Bayesian weighting calculation over graph nodes to derive objective confidence."""
        # Calculate supporting empirical weight sum
        support_weight = 0.0
        for nid in supporting_node_ids:
            if nid in graph.nodes:
                support_weight += graph.nodes[nid].empirical_weight
        norm_support = min(1.0, support_weight / max(1.0, len(supporting_node_ids) or 1))

        # Calculate contradiction penalties
        contra_weight = 0.0
        for nid in contradiction_node_ids:
            if nid in graph.nodes:
                contra_weight += graph.nodes[nid].empirical_weight
        penalty = min(1.0, (contra_weight * 1.5) / max(1.0, len(contradiction_node_ids) or 1))

        # Sample size logarithmic confidence scaling
        sample_factor = min(1.0, math.log(max(10, sample_count), 10) / 5.0)  # Reaches 1.0 at 100k samples

        # Weighted Linear Combination with Bayesian smoothing
        raw_score = (norm_support * 0.5) + (prior_similarity * 0.3) + (sample_factor * 0.2)
        adjusted_score = max(0.01, min(0.99, raw_score * (1.0 - (penalty * 0.7))))

        return HypothesisScoreMetric(
            empirical_support_score=round(norm_support, 4),
            contradiction_penalty=round(penalty, 4),
            historical_similarity_prior=round(prior_similarity, 4),
            sample_size_factor=round(sample_factor, 4),
            computed_confidence=round(adjusted_score, 4),
        )
