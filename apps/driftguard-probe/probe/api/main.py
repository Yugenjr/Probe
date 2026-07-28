"""FastAPI Application instantiation and lifecycle configuration."""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ..core.config import get_settings
from ..core.telemetry import initialize_telemetry
from ..utils.logging import setup_logging
from .routers import health_router, webhooks_router, investigations_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup telemetries and graceful shutdown cleanup loops."""
    settings = get_settings()
    setup_logging(settings)
    initialize_telemetry(settings)
    
    # Initialize and subscribe the agent runtime to the event bus
    from ..engine.runtime import get_investigation_runtime
    runtime = get_investigation_runtime()
    runtime.subscribe_to_bus()
    
    logger.info("DriftGuard Probe application startup completed. AI Investigation Engine active.")
    yield
    logger.info("DriftGuard Probe graceful shutdown completed.")


def create_app() -> FastAPI:
    """Factory creating configured FastAPI gateway application."""
    settings = get_settings()
    application = FastAPI(
        title="DriftGuard Probe",
        description="Production-grade, platform-agnostic Autonomous ML Investigation Engine",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: Configurable CORS allowed origins restriction
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(health_router)
    application.include_router(webhooks_router)
    application.include_router(investigations_router)

    return application


app = create_app()
