"""Concrete adapters implementing external platform and persistence interfaces."""
from .driftguard.client import DriftGuardRESTClient
from .mcp.client import MCPPlatformClient
from .storage.repository import LocalStateRepository

__all__ = [
    "DriftGuardRESTClient",
    "MCPPlatformClient",
    "LocalStateRepository",
]
