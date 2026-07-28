"""FastAPI investigation gateway application and asynchronous routing endpoints."""
from .main import app, create_app
from .dependencies import get_api_settings, get_api_container

__all__ = ["app", "create_app", "get_api_settings", "get_api_container"]
