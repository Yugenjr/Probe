class InferenceException(Exception):
    """Base exception for all Probe Inference Engine errors."""
    pass

class InferenceTimeoutError(InferenceException):
    """Raised when compute backend fails to return within configured timeout_seconds."""
    pass

class InferenceBackendError(InferenceException):
    """Raised when compute backend encounters HTTP errors (e.g. 503 Service Unavailable) or exhausts retries."""
    pass

class MalformedResponseError(InferenceException):
    """Raised when inference backend returns empty payloads or unparseable JSON text."""
    pass

class SchemaValidationError(InferenceException):
    """Raised when parsed JSON object violates required Pydantic target schema attributes."""
    pass

class EvidenceHallucinationError(InferenceException):
    """Raised when output references hallucinated evidence IDs not found in repository. No silent repairs permitted."""
    pass
