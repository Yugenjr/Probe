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

    # Bootstrap MCP infrastructure
    from ..mcp.bootstrap import bootstrap_mcp_registry
    from ..mcp.gateway.tool_gateway import ToolGateway
    from ..evidence.evidence_gateway import EvidenceGateway
    from ..core.di import get_container

    mcp_registry = bootstrap_mcp_registry()
    tool_gateway = ToolGateway(registry=mcp_registry)
    evidence_gateway = EvidenceGateway(tool_gateway=tool_gateway)

    container = get_container()
    container.mcp_registry = mcp_registry
    container.tool_gateway = tool_gateway
    container.evidence_gateway = evidence_gateway
    logger.info(
        "MCP ToolGateway initialized. Servers: %s",
        mcp_registry.list_servers()
    )

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
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from .routers import health_router, webhooks_router, investigations_router, mcp_router
    application.include_router(health_router)
    application.include_router(webhooks_router)
    application.include_router(investigations_router)
    application.include_router(mcp_router)

    return application



app = create_app()
