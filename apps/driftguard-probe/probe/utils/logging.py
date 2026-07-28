"""Structured logger initialization."""
import logging
import sys
from typing import Optional
from ..core.config import Settings


def setup_logging(settings: Optional[Settings] = None, level: int = logging.INFO) -> None:
    """Configure standardized stream logging format across multi-agent processes."""
    if settings and settings.debug_mode:
        level = logging.DEBUG
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = [handler]
