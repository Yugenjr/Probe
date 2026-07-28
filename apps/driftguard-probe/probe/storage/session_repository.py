import os
import json
from pathlib import Path
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


class FileSessionStore(SessionRepository):
    """File-backed session repository that persists sessions as JSON files in a workspace directory."""

    def __init__(self, directory: str = "storage/sessions"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self._storage: Dict[str, InvestigationSession] = {}
        # Pre-load existing sessions from disk
        for file_path in self.directory.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    session = InvestigationSession.model_validate(data)
                    self._storage[session.session_id] = session
            except Exception:
                pass

    async def save(self, session: InvestigationSession) -> None:
        self._storage[session.session_id] = session
        file_path = self.directory / f"{session.session_id}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(session.model_dump_json(indent=2))
        except Exception:
            pass

    async def get(self, session_id: str) -> Optional[InvestigationSession]:
        # Try in-memory cache first
        if session_id in self._storage:
            return self._storage[session_id]
        # Check disk
        file_path = self.directory / f"{session_id}.json"
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    session = InvestigationSession.model_validate(data)
                    self._storage[session_id] = session
                    return session
            except Exception:
                pass
        return None

    async def delete(self, session_id: str) -> None:
        if session_id in self._storage:
            del self._storage[session_id]
        file_path = self.directory / f"{session_id}.json"
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception:
                pass


# Alias for backward-compatibility
InMemorySessionStore = FileSessionStore

_session_repository: Optional[SessionRepository] = None


def get_session_repository() -> SessionRepository:
    """Acquire global singleton instance of session repository."""
    global _session_repository
    if _session_repository is None:
        _session_repository = FileSessionStore()
    return _session_repository
