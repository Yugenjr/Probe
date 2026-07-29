"""Agent executions persistence models."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from ..base import Base


class AgentExecution(Base):
    """Execution audit snapshot returned by a completed agent invocation."""
    
    __tablename__ = "agent_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    investigation_id: Mapped[str] = mapped_column(String(100), ForeignKey("investigations.session_id", ondelete="CASCADE"), index=True)
    agent_name: Mapped[str] = mapped_column(String(100), index=True)
    
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    
    prompt_version: Mapped[str] = mapped_column(String(50), default="v1")
    llm_model: Mapped[str] = mapped_column(String(100), default="unknown")
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    input_json: Mapped[dict] = mapped_column(JSON, default=dict)
    output_json: Mapped[dict] = mapped_column(JSON, default=dict)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
