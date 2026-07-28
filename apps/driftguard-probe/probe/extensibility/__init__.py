"""Extensibility frameworks and out-of-process plugin isolation sandboxes for DriftGuard Probe."""
from .loader import PluginLoader
from .sandbox import PluginPermissionManifest, SandboxedAdapterClient

__all__ = [
    "PluginLoader",
    "PluginPermissionManifest",
    "SandboxedAdapterClient",
]
