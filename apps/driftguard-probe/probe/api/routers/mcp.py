"""MCP management and diagnostic endpoints."""
import logging
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field

from ...core.di import get_container, Container
from ...schemas.api import APIResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/mcp", tags=["mcp"])


class ServerStatus(BaseModel):
    name: str
    status: str
    type: str
    connected: bool
    transport: str
    response_latency: int = Field(..., alias="responseLatency")
    number_of_tools: int = Field(..., alias="numberOfTools")
    last_health_check: str = Field(..., alias="lastHealthCheck")


class ToolInfo(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    server: str
    transport: str


@router.get("/servers", response_model=APIResponse, summary="List registered MCP servers and status")
async def list_mcp_servers() -> APIResponse:
    """Retrieve statuses and metadata of all registered MCP servers."""
    container = get_container()
    registry = container.mcp_registry
    
    if not registry:
        return APIResponse(status="success", data={"servers": []})

    servers_list = []
    for name in registry.list_servers():
        stype = registry.get_server_type(name)
        transport = registry.get_transport(name)
        
        # Determine status and latency
        connected = True
        latency = 0
        num_tools = 0
        if stype == "local":
            connected = True
            latency = 1  # In-process transport is sub-millisecond
            server_obj = registry.get_server(name)
            if server_obj:
                num_tools = len(server_obj.get_tools())
        else:
            connected = getattr(transport, "connected", False)
            latency = getattr(transport, "last_latency_ms", 0)
            if hasattr(transport, "_tools_cache"):
                num_tools = len(transport._tools_cache)

        servers_list.append(
            {
                "name": name,
                "status": "active" if connected else "inactive",
                "type": stype,
                "connected": connected,
                "transport": "InProcess" if stype == "local" else ("HTTP" if stype == "http" else "Process/Stdio"),
                "responseLatency": latency,
                "numberOfTools": num_tools,
                "lastHealthCheck": "Passed" if connected else "Failed"
            }
        )
    return APIResponse(status="success", data={"servers": servers_list})


@router.get("/tools", response_model=APIResponse, summary="List discovered MCP tools")
async def list_mcp_tools() -> APIResponse:
    """List all available tools grouped by MCP server."""
    container = get_container()
    registry = container.mcp_registry
    
    if not registry:
        return APIResponse(status="success", data={"tools": []})

    tools = await registry.list_tools()
    tools_list = []
    for t in tools:
        stype = registry.get_server_type(t.server)
        transport_name = "InProcess" if stype == "local" else ("HTTP" if stype == "http" else "Process/Stdio")
        tools_list.append(
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
                "server": t.server,
                "transport": transport_name
            }
        )
    return APIResponse(status="success", data={"tools": tools_list})


@router.get("/activity", response_model=APIResponse, summary="List recent MCP activity log")
async def list_mcp_activity() -> APIResponse:
    """List recent tool executions and latency logs across the platform."""
    container = get_container()
    gateway = container.evidence_gateway
    logs = gateway.get_activity_log() if gateway else []
    return APIResponse(status="success", data={"activity": logs})
