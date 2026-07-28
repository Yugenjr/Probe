from typing import List, Dict, Any
from pydantic import BaseModel, Field
from probe.storage.repository import EvidenceRepository

class EvidenceNode(BaseModel):
    node_id: str
    evidence_type: str
    source_provider: str
    confidence: float
    sha256_hash: str
    payload_summary: Dict[str, Any]

    class Config:
        frozen = True

class EvidenceEdge(BaseModel):
    source_node_id: str
    target_node_id: str
    edge_type: str = "CORRELATES_WITH"

    class Config:
        frozen = True

class GraphTopology(BaseModel):
    investigation_id: str
    nodes: List[EvidenceNode] = Field(default_factory=list)
    edges: List[EvidenceEdge] = Field(default_factory=list)

    class Config:
        frozen = True

class EvidenceGraphBuilder:
    """
    Generates graph nodes from evidence and edges from relationships.
    The graph does NOT contain business logic or AI prompts.
    It simply represents relationships as a topological structure for future reasoning agents to consume.
    """
    def __init__(self, store: EvidenceRepository):
        self._store = store

    def build_graph(self, investigation_id: str) -> GraphTopology:
        evidence_items = self._store.get_by_investigation(investigation_id)
        nodes: List[EvidenceNode] = []
        edges: List[EvidenceEdge] = []
        node_ids_seen = set()

        for ev in evidence_items:
            if ev.id not in node_ids_seen:
                node_ids_seen.add(ev.id)
                nodes.append(
                    EvidenceNode(
                        node_id=ev.id,
                        evidence_type=ev.type,
                        source_provider=ev.provider,
                        confidence=ev.confidence,
                        sha256_hash=ev.hash,
                        payload_summary={"source": ev.source, "keys": list(ev.payload.keys())}
                    )
                )

            for target_id in ev.relationships:
                edges.append(
                    EvidenceEdge(
                        source_node_id=ev.id,
                        target_node_id=target_id,
                        edge_type="CORRELATES_WITH"
                    )
                )

        return GraphTopology(
            investigation_id=investigation_id,
            nodes=nodes,
            edges=edges
        )
