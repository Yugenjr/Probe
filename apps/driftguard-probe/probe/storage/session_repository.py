import os
import json
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from probe.engine.state import InvestigationSession

# Import database session factory and repositories
from ..database.connection import async_session_factory
from ..database.repositories.investigation_repository import InvestigationRepository


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
        if session_id in self._storage:
            return self._storage[session_id]
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


class PostgresSessionStore(SessionRepository):
    """SQLAlchemy-backed session repository that persists aggregates directly in PostgreSQL."""

    async def save(self, session: InvestigationSession) -> None:
        async with async_session_factory() as db_session:
            try:
                repo = InvestigationRepository(db_session)
                await repo.save_session(session)
                await db_session.commit()
            except Exception:
                await db_session.rollback()
                raise

    async def get(self, session_id: str) -> Optional[InvestigationSession]:
        async with async_session_factory() as db_session:
            repo = InvestigationRepository(db_session)
            return await repo.get_session(session_id)

    async def delete(self, session_id: str) -> None:
        from ..database.models.investigation import Investigation
        from sqlalchemy import delete
        async with async_session_factory() as db_session:
            try:
                stmt = delete(Investigation).where(Investigation.session_id == session_id)
                await db_session.execute(stmt)
                await db_session.commit()
            except Exception:
                await db_session.rollback()
                raise

    async def list_sessions(self, model_id: Optional[str] = None, status: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[InvestigationSession]:
        async with async_session_factory() as db_session:
            repo = InvestigationRepository(db_session)
            return await repo.list_sessions(model_id=model_id, status=status, limit=limit, offset=offset)


# Alias for backward-compatibility
InMemorySessionStore = FileSessionStore

_session_repository: Optional[SessionRepository] = None


def get_session_repository() -> SessionRepository:
    """Acquire global singleton instance of session repository."""
    global _session_repository
    if _session_repository is None:
        import sys
        if "pytest" in sys.modules or os.getenv("TESTING") == "true":
            _session_repository = FileSessionStore()
        else:
            _session_repository = PostgresSessionStore()
    return _session_repository

