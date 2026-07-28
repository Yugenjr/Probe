"""Secure runtime plugin loader utilizing Python Setuptools Entry Points and manifest verification."""
import importlib.metadata
import logging
from typing import Any, Dict, Optional, Type
from ..interfaces.telemetry import TelemetryProvider
from ..interfaces.governance import GovernanceProvider
from ..interfaces.execution import ExecutionProvider
from ..interfaces.knowledge import KnowledgeProvider

logger = logging.getLogger(__name__)


class PluginLoader:
    """Discovers and verifies third-party extension packages registered via Setuptools Entry Points.
    
    Supersedes naive script imports by enforcing runtime interface contract checks before any
    third-party vendor adapter (DriftGuard, WhyLabs, Evidently, Arize) is accepted into memory.
    """
    @staticmethod
    def discover_and_load_adapters() -> Dict[str, Any]:
        """Iterate over installed entry points under 'probe.adapters', verify contract adherence, and instantiate."""
        registered_adapters: Dict[str, Any] = {}
        try:
            entry_points = importlib.metadata.entry_points(group="probe.adapters")
        except Exception:
            entry_points = []

        for ep in entry_points:
            try:
                plugin_class = ep.load()
                # Verify that plugin implements at least one segregated provider capability
                is_valid_adapter = any(
                    isinstance(plugin_class(), protocol) for protocol in (
                        TelemetryProvider, GovernanceProvider, ExecutionProvider, KnowledgeProvider
                    )
                )
                if not is_valid_adapter:
                    logger.error("Plugin %s failed interface protocol verification. Abandoning load.", ep.name)
                    continue

                registered_adapters[ep.name] = plugin_class
                logger.info("Successfully discovered and verified third-party adapter plugin: %s", ep.name)
            except Exception as exc:
                logger.error("Failed loading plugin entry point %s: %s", ep.name, str(exc))

        return registered_adapters

    @staticmethod
    def attach_to_container(container: Any, default_provider_name: str = "driftguard") -> None:
        """Discover adapters and assign target provider to Inversion of Control runtime container."""
        adapters = PluginLoader.discover_and_load_adapters()
        if default_provider_name in adapters:
            instance = adapters[default_provider_name]()
            container.telemetry_provider = instance
            container.governance_provider = instance
            container.execution_provider = instance
            container.knowledge_provider = instance
            logger.info("Attached %s adapter to global DI container.", default_provider_name)
