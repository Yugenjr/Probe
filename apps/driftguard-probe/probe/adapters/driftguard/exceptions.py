"""Custom networking exceptions for DriftGuard platform interactions."""


class DriftGuardError(Exception):
    """Base exception class for all DriftGuard client errors."""
    pass


class DriftGuardAPIError(DriftGuardError):
    """Raised when the DriftGuard REST API returns a non-200 error code."""
    def __init__(self, status_code: int, message: str):
        super().__init__(f"[HTTP {status_code}] {message}")
        self.status_code = status_code


class DriftGuardConnectionError(DriftGuardError):
    """Raised when connection timeouts or unreachable hosts occur."""
    pass
