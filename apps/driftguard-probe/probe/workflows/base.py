"""Abstract workflow definition for domain investigation state machines."""
from abc import ABC, abstractmethod
from typing import Any, Dict
from ..core.state import InvestigationState
from ..core.lifecycle import InvestigationStatus


class BaseWorkflow(ABC):
    """Abstract base class for high-level incident resolution workflows.
    
    Workflows compose multiple reasoning agents (Investigator, Researcher, Hypothesis)
    into predictable, replayable state progression loops.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifying name for supervisor selection."""
        pass

    @abstractmethod
    async def execute(self, state: InvestigationState) -> InvestigationState:
        """Execute state machine progression and transition final status."""
        pass
