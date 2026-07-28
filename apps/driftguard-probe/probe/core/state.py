"""Backwards-compatible state alias importing from v2.0 probe.engine.state."""
from ..engine.state import InvestigationSession, InvestigationState, InvestigationStatus

__all__ = [
    "InvestigationSession",
    "InvestigationState",
    "InvestigationStatus",
]
