"""Backwards-compatible supervisor alias importing from v2.0 probe.engine.orchestrator."""
from typing import Any, Optional
from ..engine.orchestrator import InvestigationOrchestrator as CoreSupervisor
from ..engine.state import InvestigationState, InvestigationStatus

__all__ = [
    "CoreSupervisor",
    "InvestigationState",
    "InvestigationStatus",
]
