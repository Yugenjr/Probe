import logging
from typing import List
from ..domain.evidence import EvidenceBundle, UniversalEvidence

logger = logging.getLogger(__name__)

class EvidenceRanker:
    """Deterministic sorting service to order evidence by relevance and confidence."""
    
    def rank(self, bundle: EvidenceBundle) -> List[UniversalEvidence]:
        logger.info("EvidenceRanker sorting evidence from EvidenceBundle")
        
        all_evidence = []
        all_evidence.extend(bundle.metrics)
        all_evidence.extend(bundle.logs)
        all_evidence.extend(bundle.repo)
        all_evidence.extend(bundle.research)
        
        # Sort by relevance_score, then confidence_weight
        # In a real system, recency and corroboration would also be mathematically scored here.
        all_evidence.sort(
            key=lambda e: (getattr(e, 'relevance_score', 0.5), getattr(e, 'confidence_weight', 0.5)),
            reverse=True
        )
        
        logger.info("EvidenceRanker sorted %d pieces of evidence.", len(all_evidence))
        return all_evidence
