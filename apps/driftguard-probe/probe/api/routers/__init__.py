"""FastAPI routing packages."""
from .health import router as health_router
from .webhooks import router as webhooks_router
from .investigations import router as investigations_router

__all__ = ["health_router", "webhooks_router", "investigations_router"]
