import datetime
import uuid
from typing import Dict, Any, Optional
from probe.investigation.states import InvestigationStatus, InvestigationRecord

class InvestigationService:
    """
    Responsible exclusively for creating investigations, assigning IDs, managing lifecycle,
    investigation state, and metadata.
    Must NOT collect evidence. Must NOT call LLMs.
    """
    def __init__(self):
        self._store: Dict[str, InvestigationRecord] = {}

    def create_investigation(self, target_resource_id: str, trigger_source: str = "automated_monitor", tenant_id: str = "default") -> str:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        # Generate stable human readable prefix with random GUID suffix
        inv_id = f"inv-{target_resource_id.lower()}-{uuid.uuid4().hex[:8]}"
        
        record = InvestigationRecord(
            investigation_id=inv_id,
            tenant_id=tenant_id,
            trigger_source=trigger_source,
            target_resource_id=target_resource_id,
            status=InvestigationStatus.CREATED,
            created_at_utc=now,
            updated_at_utc=now,
            metadata={"initial_target": target_resource_id}
        )
        self._store[inv_id] = record
        return inv_id

    def update_status(self, investigation_id: str, status: InvestigationStatus, reason: Optional[str] = None) -> InvestigationRecord:
        if investigation_id not in self._store:
            raise KeyError(f"Investigation ID '{investigation_id}' not found in runtime state.")
        record = self._store[investigation_id]
        record.status = status
        record.updated_at_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if reason:
            record.metadata["status_change_reason"] = reason
        return record

    def get_investigation(self, investigation_id: str) -> InvestigationRecord:
        if investigation_id not in self._store:
            raise KeyError(f"Investigation ID '{investigation_id}' not found in runtime state.")
        return self._store[investigation_id]
