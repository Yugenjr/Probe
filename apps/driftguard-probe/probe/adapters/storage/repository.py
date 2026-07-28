"""Local filesystem and SQLite state storage repository."""
import logging
from typing import Any, Dict, List, Optional
from ...interfaces.storage import StorageProvider

logger = logging.getLogger(__name__)


class LocalStateRepository(StorageProvider):
    """InMemory or local database repository preserving investigation runtime states and reports."""
    def __init__(self):
        self._states: Dict[str, Dict[str, Any]] = {}

    async def save_state(self, investigation_id: str, state_data: Dict[str, Any]) -> None:
        """Store active runtime session payload."""
        logger.debug("Persisting runtime state for %s", investigation_id)
        self._states[investigation_id] = state_data
        # TODO: Implementation pending for durable SQLite/Postgres serialization

    async def load_state(self, investigation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve existing execution state payload."""
        return self._states.get(investigation_id)

    async def list_investigations(self, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """Return array of persisted historical investigation dictionaries."""
        all_states = list(self._states.values())
        return all_states[skip: skip + limit]
