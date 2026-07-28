"""Common utility string helpers and identifier generators."""
import uuid
from datetime import datetime, timezone


def generate_uuid() -> str:
    """Return secure randomly generated standard UUID4 string."""
    return str(uuid.uuid4())


def current_timestamp_iso() -> str:
    """Return UTC current timestamp in ISO 8601 string presentation."""
    return datetime.now(timezone.utc).isoformat()
