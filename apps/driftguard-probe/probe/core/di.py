"""Dependency injection runtime container enforcing interface segregation."""
from typing import Optional, TYPE_CHECKING
from .config import Settings, get_settings
from ..interfaces.adapter import PlatformProvider
from ..interfaces.telemetry import TelemetryProvider
from ..interfaces.governance import GovernanceProvider
from ..interfaces.execution import ExecutionProvider
from ..interfaces.llm import LLMProvider
from ..interfaces.memory import MemoryProvider
from ..interfaces.storage import StorageProvider
from ..mcp.registry.server_registry import ServerRegistry
from ..mcp.gateway.tool_gateway import ToolGateway
from ..evidence.evidence_gateway import EvidenceGateway


class Container:
    """Inversion of Control runtime container managing segregated providers and capabilities.

    Ensures zero coupling between core reasoning workflows, analytical tools, and concrete vendors.
    """
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.telemetry_provider: Optional[TelemetryProvider] = None
        self.governance_provider: Optional[GovernanceProvider] = None
        self.execution_provider: Optional[ExecutionProvider] = None
        self.llm_provider: Optional[LLMProvider] = None
        self.memory_provider: Optional[MemoryProvider] = None
        self.storage_provider: Optional[StorageProvider] = None
        # MCP infrastructure — injected at application startup
        self.mcp_registry: Optional["ServerRegistry"] = None
        self.tool_gateway: Optional["ToolGateway"] = None
        self.evidence_gateway: Optional["EvidenceGateway"] = None
        from ..mcp.capability import CapabilityRegistry
        self.capability_registry: CapabilityRegistry = CapabilityRegistry()
        
        # Database repositories — injected at startup
        from ..database.repositories.investigation_repository import InvestigationRepository
        from ..database.repositories.mcp_repository import McpRepository
        self.investigation_repository: Optional[InvestigationRepository] = None
        self.mcp_repository: Optional[McpRepository] = None




    @property
    def platform_provider(self) -> Optional[PlatformProvider]:
        """Convenience accessor for aggregate full-stack platforms (e.g. DriftGuard)."""
        if isinstance(self.telemetry_provider, PlatformProvider):
            return self.telemetry_provider
        return None

    @platform_provider.setter
    def platform_provider(self, provider: Optional[PlatformProvider]) -> None:
        """Assign aggregate platform provider to all three segregated capability boundaries."""
        self.telemetry_provider = provider
        self.governance_provider = provider
        self.execution_provider = provider


_global_container: Optional[Container] = None


def get_container() -> Container:
    """Acquire global singleton DI container instance."""
    global _global_container
    if _global_container is None:
        _global_container = Container()
    return _global_container


def reset_container() -> None:
    """Reset container (utilized exclusively during isolated unit test runs)."""
    global _global_container
    _global_container = None
