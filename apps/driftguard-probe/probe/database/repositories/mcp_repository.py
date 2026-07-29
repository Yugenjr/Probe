"""SQLAlchemy-backed repository managing MCP integrations and dynamic tool execution records."""
import logging
import time
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, desc
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository
from ..models.mcp import McpServerMetadata as DBMcpServer, McpTool as DBMcpTool, McpExecution as DBMcpExecution

logger = logging.getLogger(__name__)


class McpRepository(BaseRepository):
    """Manages transactional records for all registered servers, tools, and executions."""

    async def save_mcp_server(
        self,
        server_name: str,
        transport: str,
        status: str = "active",
        latency_ms: int = 0,
        capabilities: Optional[List[str]] = None
    ) -> None:
        """Register or update active status/health metrics of an MCP server."""
        query = select(DBMcpServer).where(DBMcpServer.server_name == server_name)
        res = await self.session.execute(query)
        db_srv = res.scalar_one_or_none()

        srv_data = {
            "transport": transport,
            "status": status,
            "latency_ms": latency_ms,
            "capabilities_json": {"capabilities": capabilities or []},
            "last_health_check": datetime.utcnow()
        }

        if not db_srv:
            db_srv = DBMcpServer(server_name=server_name, **srv_data)
            self.session.add(db_srv)
            logger.debug("[McpRepo] Registered server metadata: %s", server_name)
        else:
            for k, v in srv_data.items():
                setattr(db_srv, k, v)
            logger.debug("[McpRepo] Updated server status metrics: %s", server_name)
        await self.session.flush()

    async def list_mcp_servers(self) -> List[Dict[str, Any]]:
        """List health and latencies of all registered servers."""
        query = select(DBMcpServer)
        res = await self.session.execute(query)
        servers = []
        for row in res.scalars():
            servers.append({
                "name": row.server_name,
                "transport": row.transport,
                "version": row.version,
                "status": row.status,
                "capabilities": row.capabilities_json.get("capabilities", []),
                "last_health_check": row.last_health_check.replace(tzinfo=timezone.utc).isoformat(),
                "responseLatency": row.latency_ms,
                "connected": row.status == "active"
            })
        return servers

    async def log_mcp_execution(
        self,
        investigation_id: str,
        server_name: str,
        tool_name: str,
        request_payload: Dict[str, Any],
        response_payload: Dict[str, Any],
        latency_ms: int,
        retry_count: int = 0,
        status: str = "success",
        error_message: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> None:
        """Log a detailed tool call execution for audit compliance and debugging."""
        db_exec = DBMcpExecution(
            investigation_id=investigation_id,
            server_name=server_name,
            tool_name=tool_name,
            request_json=request_payload,
            response_json=response_payload,
            started_at=datetime.utcnow(),
            finished_at=datetime.utcnow(),
            latency_ms=latency_ms,
            retry_count=retry_count,
            status=status,
            error_message=error_message,
            correlation_id=correlation_id or f"corr-{int(time.time())}"
        )
        self.session.add(db_exec)
        await self.session.flush()

    async def list_mcp_executions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent executions log across all integrations."""
        query = select(DBMcpExecution).order_by(desc(DBMcpExecution.started_at)).limit(limit)
        res = await self.session.execute(query)
        executions = []
        for row in res.scalars():
            executions.append({
                "timestamp": int(row.started_at.replace(tzinfo=timezone.utc).timestamp()),
                "server": row.server_name,
                "tool": row.tool_name,
                "duration_ms": row.latency_ms,
                "success": row.status == "success",
                "request": row.request_json,
                "response": row.response_json,
                "error": row.error_message,
                "correlation_id": row.correlation_id
            })
        return executions
