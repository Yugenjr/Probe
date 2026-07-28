"""Dynamic plugin loader supporting zero-modification architectural extensibility."""
import importlib
import logging
from typing import List

logger = logging.getLogger(__name__)


class PluginLoader:
    """Loads third-party adapters (WhyLabsPlugin, ArizePlugin) and custom reasoning agents dynamically."""
    def __init__(self):
        self.loaded_plugins: List[str] = []

    def load_plugin(self, module_path: str) -> None:
        """Import external plugin Python module and trigger registration hooks."""
        try:
            mod = importlib.import_module(module_path)
            if hasattr(mod, "register_plugin"):
                mod.register_plugin()
            self.loaded_plugins.append(module_path)
            logger.info("Successfully loaded extension plugin: %s", module_path)
        except ImportError as exc:
            logger.error("Failed to dynamically import plugin module '%s': %s", module_path, str(exc))
            raise
        # TODO: Implementation pending for entry_points verification and security sandboxing


_global_loader = PluginLoader()


def get_plugin_loader() -> PluginLoader:
    """Acquire singleton plugin loader instance."""
    return _global_loader
