"""Storage provider protocol abstractions."""
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


@runtime_checkable
class StorageProvider(Protocol):
    """Abstract interface for persisting runtime state and diagnostic reports."""

    async def save_state(self, investigation_id: str, state_data: Dict[str, Any]) -> None:
        """Persist or update active investigation lifecycle state."""
        ...

    async def load_state(self, investigation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve existing investigation execution state."""
        ...

    async def list_investigations(self, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """List historical or active investigation summaries."""
        ...
