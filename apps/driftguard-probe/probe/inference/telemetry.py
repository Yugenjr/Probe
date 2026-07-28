import datetime
import uuid
from typing import List, Optional
from pydantic import BaseModel, Field

class InferenceTelemetryRecord(BaseModel):
    """
    Operational infrastructure log record.
    SECURITY PROTOCOL: Never logs evidence payloads, secrets, authentication tokens, or sensitive investigation data.
    Contains strictly operational compute metadata.
    """
    record_id: str = Field(default_factory=lambda: f"tel-{uuid.uuid4().hex[:10]}")
    timestamp_utc: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    model_identifier: str
    request_duration_ms: float
    token_usage_approx: int
    response_bytes_size: int
    retry_count: int
    success: bool
    failure_error_type: Optional[str] = None
    endpoint_hostname: str

    class Config:
        frozen = True

class TelemetryCollector:
    """
    In-memory / repository sink for capturing operational infrastructure metrics without secret leakage.
    """
    def __init__(self):
        self._records: List[InferenceTelemetryRecord] = []

    def log_record(self, record: InferenceTelemetryRecord) -> None:
        self._records.append(record)

    def get_records(self) -> List[InferenceTelemetryRecord]:
        return list(self._records)

    def verify_no_secrets_leaked(self, secret_token: str, sensitive_payload_keywords: List[str]) -> bool:
        """
        Security verification utility. Asserts that secret authentication tokens or investigation payload
        strings never exist in serialized telemetry records.
        """
        for r in self._records:
            dumped = r.model_dump_json()
            if secret_token in dumped:
                return False
            for kw in sensitive_payload_keywords:
                if kw in dumped and kw != "":
                    return False
        return True
