#!/usr/bin/env python3
"""Standalone launch script starting the DriftGuard Probe API gateway server."""
import uvicorn
from probe.core.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    print(f"Launching DriftGuard Probe on {settings.probe_host}:{settings.probe_port}...")
    uvicorn.run(
        "probe.api.main:app",
        host=settings.probe_host,
        port=settings.probe_port,
        reload=settings.debug_mode,
    )
