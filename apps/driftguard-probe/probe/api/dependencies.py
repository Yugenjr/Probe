"""FastAPI Dependency Injection providers."""
from functools import lru_cache
from typing import Generator
from ..core.config import Settings, get_settings
from ..core.di import Container, get_container


def get_api_settings() -> Settings:
    """FastAPI depends provider yielding singleton configuration settings."""
    return get_settings()


def get_api_container() -> Container:
    """FastAPI depends provider yielding inversion of control provider container."""
    return get_container()
