from typing import Type, Any, Dict, List, TypeVar, Optional
from pydantic import BaseModel, ValidationError

from probe.storage.repository import EvidenceRepository
from .exceptions import SchemaValidationError, EvidenceHallucinationError

T = TypeVar("T", bound=BaseModel)

class SchemaValidator:
    """
    Enforces Pydantic structural schema validity and empirical evidence ID integrity.
    Never silently repairs hallucinated references; rejects malformed outputs immediately.
    """
    @classmethod
    def validate_and_instantiate(
        cls,
        payload_dict: Dict[str, Any],
        target_model: Type[T],
        repository: Optional[EvidenceRepository] = None
    ) -> T:
        # 1. Structural Pydantic Validation
        try:
            instance = target_model.model_validate(payload_dict)
        except ValidationError as e:
            raise SchemaValidationError(
                f"[SchemaValidator] Response failed target schema verification ({target_model.__name__}):\n{str(e)}"
            ) from e

        # 2. Strict Evidence ID Integrity Audit (No Hallucinations Permitted)
        if repository is not None:
            referenced_ids: List[str] = []
            cls._extract_evidence_ids(payload_dict, referenced_ids)
            
            hallucinated_ids = []
            for ev_id in set(referenced_ids):
                # We inspect any ID formatted as ev-... or in supporting evidence lists
                if ev_id.startswith("ev-") and repository.get_by_id(ev_id) is None:
                    hallucinated_ids.append(ev_id)

            if hallucinated_ids:
                raise EvidenceHallucinationError(
                    f"[SchemaValidator] Rejected generation due to hallucinated evidence IDs not found in storage: {sorted(hallucinated_ids)}. Silent repair is strictly prohibited."
                )

        return instance

    @classmethod
    def _extract_evidence_ids(cls, data: Any, accumulator: List[str]) -> None:
        if isinstance(data, dict):
            for k, v in data.items():
                if k in ("supporting_evidence_ids", "contradicting_evidence_ids", "evidence_id", "sha256_parent_evidence_ids"):
                    if isinstance(v, list):
                        accumulator.extend([str(x) for x in v if x])
                    elif isinstance(v, str):
                        accumulator.append(v)
                else:
                    cls._extract_evidence_ids(v, accumulator)
        elif isinstance(data, list):
            for item in data:
                cls._extract_evidence_ids(item, accumulator)
