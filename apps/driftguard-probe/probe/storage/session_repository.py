"""SessionRepository interface and InMemorySessionStore implementation for persisting active investigation sessions."""
from abc import ABC, abstractmethod
from typing import Dict, Optional
from probe.engine.state import InvestigationSession


class SessionRepository(ABC):
    """Abstract interface defining required capabilities for session storage."""

    @abstractmethod
    async def save(self, session: InvestigationSession) -> None:
        """Persist or update an InvestigationSession."""
        pass

    @abstractmethod
    async def get(self, session_id: str) -> Optional[InvestigationSession]:
        """Retrieve an InvestigationSession by ID."""
        pass

    @abstractmethod
    async def delete(self, session_id: str) -> None:
        """Remove an InvestigationSession from storage."""
        pass


class InMemorySessionStore(SessionRepository):
    """Temporary in-memory backing for session repository, ensuring simple future database migration."""

    def __init__(self):
        self._storage: Dict[str, InvestigationSession] = {}

    async def save(self, session: InvestigationSession) -> None:
        self._storage[session.session_id] = session

    async def get(self, session_id: str) -> Optional[InvestigationSession]:
        return self._storage.get(session_id)

    async def delete(self, session_id: str) -> None:
        if session_id in self._storage:
            del self._storage[session_id]


_session_repository: Optional[SessionRepository] = None


def get_session_repository() -> SessionRepository:
    """Acquire global singleton instance of session repository."""
    global _session_repository
    if _session_repository is None:
        _session_repository = InMemorySessionStore()
    return _session_repository
