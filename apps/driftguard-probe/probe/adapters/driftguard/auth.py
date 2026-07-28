"""DriftGuard REST authentication header helper."""
from typing import Dict, Optional


class DriftGuardAuth:
    """Encapsulates secure API Key token formatting for outgoing HTTP headers."""
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    def get_headers(self) -> Dict[str, str]:
        """Generate authentication headers without exposing keys in plain logs."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers
