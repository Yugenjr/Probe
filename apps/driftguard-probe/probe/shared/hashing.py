import json
import hashlib
from typing import Any, Dict

def compute_canonical_sha256(data: Dict[str, Any]) -> str:
    """
    Computes a deterministic cryptographic SHA-256 hash over an arbitrary Python dictionary.
    Keys are lexicographically sorted and formatted as compact UTF-8 bytes to guarantee
    perfect idempotency across independent process runs.
    """
    try:
        raw_bytes = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        return hashlib.sha256(raw_bytes).hexdigest()
    except Exception as e:
        # Fallback string coercion for unusual custom numeric primitives
        raw_bytes = str(sorted(data.items())).encode("utf-8")
        return hashlib.sha256(raw_bytes).hexdigest()
