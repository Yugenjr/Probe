"""Abstract interfaces defining external platform adapter and vendor capabilities."""
from typing import Protocol, runtime_checkable
from .context import ResourceContext
from .telemetry import TelemetryProvider
from .governance import GovernanceProvider
from .execution import ExecutionProvider
from .knowledge import KnowledgeProvider


@runtime_checkable
class PlatformProvider(TelemetryProvider, GovernanceProvider, ExecutionProvider, KnowledgeProvider, Protocol):
    """Aggregate protocol uniting Telemetry, Governance, Execution, and Knowledge capabilities.
    
    Full-stack platforms satisfy this aggregate protocol, whereas pure observability or CI/CD platforms
    implement exclusively their relevant segregated interface boundaries.
    """
    pass


__all__ = [
    "ResourceContext",
    "TelemetryProvider",
    "GovernanceProvider",
    "ExecutionProvider",
    "KnowledgeProvider",
    "PlatformProvider",
]
