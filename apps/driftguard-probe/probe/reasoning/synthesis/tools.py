from typing import List, Dict, Any, Tuple
from probe.storage.repository import EvidenceRepository
from probe.graph.builder import GraphTopology

class SynthesisTools:
    """
    Deterministic domain tools for CausalSynthesisAgent.
    Performs graph topology traversal, temporal ordering, and strict ID validation
    without invoking generative prompts.
    """
    @staticmethod
    def extract_correlated_clusters(topology: GraphTopology, repository: EvidenceRepository) -> List[Dict[str, Any]]:
        """
        Traverses directional edges (CORRELATES_WITH) in the Evidence Graph to bundle related
        evidence records into cohesive diagnostic clusters.
        """
        adjacency: Dict[str, List[str]] = {}
        for edge in topology.edges:
            if edge.source_node_id not in adjacency:
                adjacency[edge.source_node_id] = []
            adjacency[edge.source_node_id].append(edge.target_node_id)
            # Make bidirectional for cluster grouping
            if edge.target_node_id not in adjacency:
                adjacency[edge.target_node_id] = []
            adjacency[edge.target_node_id].append(edge.source_node_id)

        visited = set()
        clusters: List[Dict[str, Any]] = []

        for node in topology.nodes:
            if node.node_id not in visited:
                cluster_ids = []
                queue = [node.node_id]
                visited.add(node.node_id)
                
                while queue:
                    curr = queue.pop(0)
                    cluster_ids.append(curr)
                    for nbr in adjacency.get(curr, []):
                        if nbr not in visited:
                            visited.add(nbr)
                            queue.append(nbr)
                            
                items = []
                for cid in cluster_ids:
                    ev = repository.get_by_id(cid)
                    if ev:
                        items.append({
                            "id": ev.id,
                            "type": ev.type,
                            "source": ev.source,
                            "timestamp": ev.timestamp,
                            "payload_keys": list(ev.payload.keys()),
                            "payload_summary": ev.payload
                        })
                        
                if items:
                    clusters.append({
                        "cluster_size": len(items),
                        "primary_types": list(set(i["type"] for i in items)),
                        "evidence_items": items
                    })

        # Sort largest cluster first
        clusters.sort(key=lambda x: x["cluster_size"], reverse=True)
        return clusters

    @staticmethod
    def detect_temporal_ordering(repository: EvidenceRepository, origin: str) -> List[Dict[str, Any]]:
        """
        Chronologically sorts evidence artifacts by UTC timestamp to reveal cause-and-effect timeline progression.
        """
        items = repository.get_by_investigation(origin)
        sorted_items = sorted(items, key=lambda x: str(x.timestamp))
        timeline = []
        for ev in sorted_items:
            timeline.append({
                "timestamp": ev.timestamp,
                "evidence_id": ev.id,
                "type": ev.type,
                "source": ev.source
            })
        return timeline

    @staticmethod
    def verify_evidence_ids_exist(evidence_ids: List[str], repository: EvidenceRepository) -> Tuple[bool, List[str], List[str]]:
        """
        Strict antifraud validator. Checks if referenced evidence IDs actually exist in repository.
        Returns (is_all_valid, valid_ids_list, hallucinated_ids_list).
        """
        valid = []
        hallucinated = []
        for id_ in evidence_ids:
            if repository.get_by_id(id_) is not None:
                valid.append(id_)
            else:
                hallucinated.append(id_)
        return (len(hallucinated) == 0, valid, hallucinated)
