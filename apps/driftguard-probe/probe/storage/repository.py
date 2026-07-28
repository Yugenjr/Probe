from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from probe.evidence.base import Evidence

class EvidenceRepository(ABC):
    @abstractmethod
    def append(self, evidence: Evidence) -> bool:
        pass

    @abstractmethod
    def get_by_id(self, evidence_id: str) -> Optional[Evidence]:
        pass

    @abstractmethod
    def get_by_investigation(self, origin: str) -> List[Evidence]:
        pass

    @abstractmethod
    def find_related(self, evidence_id: str) -> List[Evidence]:
        pass

class InMemoryEvidenceStore(EvidenceRepository):
    """
    Immutable, append-only, versioned persistence layer for extracted Evidence objects.
    If an item with identical ID/SHA-256 hash is appended twice, it is treated as a 
    no-op idempotent success without mutating existing records.
    """
    def __init__(self):
        self._store: Dict[str, Evidence] = {}
        self._origin_idx: Dict[str, List[str]] = {}

    def append(self, evidence: Evidence) -> bool:
        if evidence.id in self._store:
            # Idempotent convergence: exact duplicate already present
            existing_hash = self._store[evidence.id].hash
            if existing_hash != evidence.hash:
                raise ValueError(f"[EvidenceStore] Hash collision or tampering on ID {evidence.id}: {existing_hash} != {evidence.hash}")
            return False

        self._store[evidence.id] = evidence
        if evidence.origin not in self._origin_idx:
            self._origin_idx[evidence.origin] = []
        self._origin_idx[evidence.origin].append(evidence.id)
        return True

    def get_by_id(self, evidence_id: str) -> Optional[Evidence]:
        return self._store.get(evidence_id)

    def get_by_investigation(self, origin: str) -> List[Evidence]:
        ids = self._origin_idx.get(origin, [])
        return [self._store[id_] for id_ in ids if id_ in self._store]

    def find_related(self, evidence_id: str) -> List[Evidence]:
        results = []
        for item in self._store.values():
            if evidence_id in item.relationships or item.id == evidence_id:
                results.append(item)
        return results
