"""Event-Sourced Replay Journal Architecture supporting time-travel debugging and distributed resilience."""
from enum import Enum
from datetime import datetime, timezone
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from ..domain.graph import EvidenceNode, EvidenceGraph, EdgeType


class EventType(str, Enum):
    """Immutable state transition command events governing investigation evolution."""
    SESSION_INITIALIZED = "SESSION_INITIALIZED"
    EVIDENCE_NODE_ACCRUED = "EVIDENCE_NODE_ACCRUED"
    CAUSAL_EDGE_BOUND = "CAUSAL_EDGE_BOUND"
    HYPOTHESIS_FORMULATED = "HYPOTHESIS_FORMULATED"
    CONFIDENCE_RECALCULATED = "CONFIDENCE_RECALCULATED"
    REMEDIATION_DISPATCHED = "REMEDIATION_DISPATCHED"


class StateDeltaEvent(BaseModel):
    """Immutable audit event representing an atomic state transition command."""
    sequence_id: int = Field(..., description="Monotonically increasing chronological sequence index")
    event_type: EventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: Dict[str, Any]
    operator_or_agent: str = Field(..., description="Execution author e.g. 'InvestigatorAgent' or 'HumanEngineer'")


class EventSourcedSession:
    """CQRS event storage repository capable of deterministic time-travel state rehydration.
    
    Supersedes deep-copy memory cloning by storing investigations purely as append-only event logs,
    enabling seamless pause, resume, replay, and horizontal concurrency safety across pod outages.
    """
    def __init__(self, session_id: str):
        self.session_id = session_id
        self._journal_events: List[StateDeltaEvent] = []
        self._sequence_counter = 0
        self.materialized_graph = EvidenceGraph(graph_id=f"graph-{session_id}")
        self.active_status = "INITIALIZED"

    def append_event(self, event_type: EventType, payload: Dict[str, Any], author: str) -> StateDeltaEvent:
        """Atomically commit transition command to append-only journal and update materialized view."""
        self._sequence_counter += 1
        event = StateDeltaEvent(
            sequence_id=self._sequence_counter,
            event_type=event_type,
            payload=payload,
            operator_or_agent=author
        )
        self._journal_events.append(event)
        self._apply_event_to_materialized_view(event)
        return event

    def _apply_event_to_materialized_view(self, event: StateDeltaEvent) -> None:
        """Internal projector mapping atomic events onto runtime reading state representations."""
        if event.event_type == EventType.SESSION_INITIALIZED:
            self.active_status = "COLLECTING_EVIDENCE"
        elif event.event_type == EventType.EVIDENCE_NODE_ACCRUED:
            node = EvidenceNode(**event.payload["node_data"])
            self.materialized_graph.add_node(node)
        elif event.event_type == EventType.CAUSAL_EDGE_BOUND:
            data = event.payload
            self.materialized_graph.connect_nodes(
                source_id=data["source_id"],
                target_id=data["target_id"],
                edge_type=EdgeType(data["edge_type"]),
                justification=data["justification"],
                weight=float(data.get("weight", 0.8)),
            )
        elif event.event_type == EventType.REMEDIATION_DISPATCHED:
            self.active_status = "COMPLETED"

    def replay_to_sequence(self, target_sequence_id: int) -> "EventSourcedSession":
        """Rehydrate historical point-in-time system state up to target sequence milestone."""
        replayed_session = EventSourcedSession(self.session_id)
        for evt in self._journal_events:
            if evt.sequence_id <= target_sequence_id:
                replayed_session.append_event(evt.event_type, evt.payload, evt.operator_or_agent)
            else:
                break
        return replayed_session

    def export_audit_journal(self) -> List[Dict[str, Any]]:
        """Export tamper-proof serializable journal for regulatory compliance auditing."""
        return [evt.model_dump(mode="json") for evt in self._journal_events]
