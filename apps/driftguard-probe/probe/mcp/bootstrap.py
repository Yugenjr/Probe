"""Bootstrap loader for MCP servers configuration."""
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


from .registry.server_registry import ServerRegistry
from .servers.knowledge.server import KnowledgeServer
from .transport.remote import HttpTransport, ProcessTransport

logger = logging.getLogger(__name__)


def bootstrap_mcp_registry(config_path: Optional[str] = None) -> ServerRegistry:
    """Load configuration and initialize registry with local and remote transports.

    Args:
        config_path: Path to the mcp_config.yaml. Defaults to probe/config/mcp_config.yaml.
    """
    registry = ServerRegistry()

    if config_path is None:
        # Check standard locations
        base_dir = Path(__file__).resolve().parents[2]
        config_path = str(base_dir / "probe" / "config" / "mcp_config.yaml")

    if not os.path.exists(config_path):
        logger.warning("[MCP Bootstrap] Config file not found at %s. Registering default local KnowledgeServer.", config_path)
        registry.register(KnowledgeServer())
        return registry

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            
        servers_config: Dict[str, Any] = config.get("servers", {})
        for name, cfg in servers_config.items():
            stype = cfg.get("type", "local")
            if stype == "local":
                if name == "knowledge":
                    registry.register(KnowledgeServer())
                else:
                    logger.warning("[MCP Bootstrap] Unknown local server: %s", name)
            elif stype == "http":
                url = cfg.get("url")
                if not url:
                    logger.error("[MCP Bootstrap] Server %s has type http but missing url config.", name)
                    continue
                headers = cfg.get("headers", {})
                transport = HttpTransport(server_name=name, url=url, headers=headers)
                registry.register(server_or_name=name, transport=transport, server_type="http")
            elif stype == "process":
                command = cfg.get("command")
                args = cfg.get("args", [])
                env = cfg.get("env", {})
                if not command:
                    logger.error("[MCP Bootstrap] Server %s has type process but missing command config.", name)
                    continue
                transport = ProcessTransport(server_name=name, command=command, args=args, env=env)
                registry.register(server_or_name=name, transport=transport, server_type="process")
            else:
                logger.error("[MCP Bootstrap] Unknown server type '%s' for %s", stype, name)

    except Exception as e:
        logger.error("[MCP Bootstrap] Error loading MCP configuration: %s", e, exc_info=True)
        # Safe fallback
        registry.register(KnowledgeServer())

    return registry
