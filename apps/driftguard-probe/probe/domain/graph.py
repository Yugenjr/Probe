"""Directed Acyclic Evidence Graph architecture enabling topologic causal reasoning."""
from enum import Enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EdgeType(str, Enum):
    """Relational designations uniting evidence nodes across causal problem lineages."""
    CAUSAL_TO = "CAUSAL_TO"               # Direct root-cause causation e.g. Feature Drift -> Latency Spike
    CORRELATED_WITH = "CORRELATED_WITH"   # Temporal co-occurrence without confirmed causality
    CONTRADICTS = "CONTRADICTS"           # Conflicting telemetry empirical observations
    SUPPORTED_BY = "SUPPORTED_BY"         # Secondary operational runbook validation


class EvidenceNode(BaseModel):
    """Immutable foundational node representing a singular validated evidentiary discovery."""
    node_id: str = Field(..., description="Cryptographic SHA-256 hash of evidentiary item contents")
    evidence_type: str = Field(..., description="Domain item taxonomy e.g. 'drift_stats' or 'metric_curve'")
    source_provider: str
    summary: str
    empirical_weight: float = Field(default=1.0, ge=0.0, le=1.0)
    attributes: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvidenceEdge(BaseModel):
    """Directed connection mapping relationship semantics between two evidence nodes."""
    edge_id: str = Field(..., description="Unique edge binding identifier")
    source_node_id: str
    target_node_id: str
    edge_type: EdgeType
    confidence_weight: float = Field(default=0.8, ge=0.0, le=1.0)
    justification: str = Field(..., description="Mathematical or chronological justification for edge assertion")


class EvidenceGraph(BaseModel):
    """Topologic evidence network superseding flat arrays to enable deep root cause tracing."""
    graph_id: str
    nodes: Dict[str, EvidenceNode] = Field(default_factory=dict)
    edges: List[EvidenceEdge] = Field(default_factory=list)

    def add_node(self, node: EvidenceNode) -> None:
        """Safely attach evidentiary node to graph structure."""
        self.nodes[node.node_id] = node

    def connect_nodes(self, source_id: str, target_id: str, edge_type: EdgeType, justification: str, weight: float = 0.8) -> None:
        """Establish directed relational causal link between existing graph nodes."""
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError(f"Cannot establish relational link; missing target node IDs in graph: {source_id} -> {target_id}")
        
        edge_id = f"edge-{source_id[:6]}-{target_id[:6]}-{len(self.edges)}"
        self.edges.append(EvidenceEdge(
            edge_id=edge_id,
            source_node_id=source_id,
            target_node_id=target_id,
            edge_type=edge_type,
            confidence_weight=weight,
            justification=justification
        ))

    def extract_causal_path(self, target_node_id: str) -> List[EvidenceNode]:
        """Traverse upstream directed edges to isolate root cause lineage leading to anomaly node."""
        path: List[EvidenceNode] = []
        current = target_node_id
        visited = set()
        while current in self.nodes and current not in visited:
            visited.add(current)
            path.append(self.nodes[current])
            parents = [e.source_node_id for e in self.edges if e.target_node_id == current and e.edge_type == EdgeType.CAUSAL_TO]
            if not parents:
                break
            current = parents[0]  # Follow primary causal parent vector
        return path[::-1]  # Return chronologically ordered root-to-symptom path
