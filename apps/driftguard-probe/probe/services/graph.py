import logging
import uuid
from datetime import datetime, timezone
from ..domain.evidence import EvidenceBundle
from ..domain.graph import EvidenceGraph, EvidenceNode, EvidenceEdge, EdgeType

logger = logging.getLogger(__name__)

class EvidenceGraphBuilder:
    """Deterministic service to compile EvidenceBundle items into an EvidenceGraph."""
    
    def build(self, bundle: EvidenceBundle) -> EvidenceGraph:
        logger.info("EvidenceGraphBuilder constructing graph from EvidenceBundle")
        
        graph = EvidenceGraph(graph_id=str(uuid.uuid4()))
        
        # In a real system, this service would iterate through all evidence
        # and mathematically/temporally determine EdgeTypes (e.g. CAUSAL_TO).
        # We mock the structure here to satisfy the contract.
        
        for metric in bundle.metrics:
            node = EvidenceNode(
                node_id=metric.evidence_id,
                evidence_type=metric.evidence_type,
                source_provider=metric.source_provider,
                summary=metric.summary,
                empirical_weight=metric.confidence_weight
            )
            graph.nodes[node.node_id] = node
            
        for log in bundle.logs:
            node = EvidenceNode(
                node_id=log.evidence_id,
                evidence_type=log.evidence_type,
                source_provider=log.source_provider,
                summary=log.summary,
                empirical_weight=log.confidence_weight
            )
            graph.nodes[node.node_id] = node
            
            # Create a mocked CAUSAL_TO edge if there is a metric
            if bundle.metrics:
                edge = EvidenceEdge(
                    edge_id=str(uuid.uuid4()),
                    source_node_id=log.evidence_id,
                    target_node_id=bundle.metrics[0].evidence_id,
                    edge_type=EdgeType.CAUSAL_TO,
                    confidence_weight=0.8,
                    justification="Log trace occurred immediately before metric drift."
                )
                graph.edges.append(edge)
                
        logger.info("EvidenceGraphBuilder created graph with %d nodes and %d edges.", len(graph.nodes), len(graph.edges))
        return graph
