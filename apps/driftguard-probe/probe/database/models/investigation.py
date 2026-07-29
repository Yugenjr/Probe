"""Investigation session models."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from ..base import Base


class Investigation(Base):
    """SQLAlchemy model representing the active ML incident investigation session."""
    
    __tablename__ = "investigations"

    id: Mapped[str] = mapped_column(String(100), primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    investigation_id: Mapped[str] = mapped_column(String(100), index=True)
    incident_id: Mapped[str] = mapped_column(String(100), index=True)
    model_id: Mapped[str] = mapped_column(String(100), index=True)
    model_version: Mapped[str] = mapped_column(String(50), default="latest")
    status: Mapped[str] = mapped_column(String(50), index=True)
    priority: Mapped[str] = mapped_column(String(30), default="medium")
    
    started_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    trigger_type: Mapped[str] = mapped_column(String(100), default="manual")
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    final_root_cause: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Full Graph Persistence
    raw_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    investigation_context: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    remediation_plan: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
