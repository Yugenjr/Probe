"""MCP dynamic configuration registries and execution log models."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from ..base import Base


class McpServerMetadata(Base):
    """Configuration register and operational status metadata of MCP servers."""
    
    __tablename__ = "mcp_servers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    server_name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    transport: Mapped[str] = mapped_column(String(50)) # e.g. "local", "http", "process"
    version: Mapped[str] = mapped_column(String(50), default="1.0.0")
    status: Mapped[str] = mapped_column(String(50), default="active") # active, inactive
    capabilities_json: Mapped[dict] = mapped_column(JSON, default=dict) # List of capacities advertised
    last_health_check: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)


class McpTool(Base):
    """Exposed schemas of discovered MCP tools."""
    
    __tablename__ = "mcp_tools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    server_name: Mapped[str] = mapped_column(String(100), index=True)
    tool_name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parameters_json: Mapped[dict] = mapped_column(JSON, default=dict)


class McpExecution(Base):
    """Audit log tracking every single tool invocation for replay and telemetry."""
    
    __tablename__ = "mcp_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    investigation_id: Mapped[str] = mapped_column(String(100), ForeignKey("investigations.session_id", ondelete="CASCADE"), index=True)
    server_name: Mapped[str] = mapped_column(String(100), index=True)
    tool_name: Mapped[str] = mapped_column(String(100), index=True)
    
    request_json: Mapped[dict] = mapped_column(JSON, default=dict)
    response_json: Mapped[dict] = mapped_column(JSON, default=dict)
    
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    
    status: Mapped[str] = mapped_column(String(50), default="success", index=True) # success, failed
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    correlation_id: Mapped[str] = mapped_column(String(100), index=True)
