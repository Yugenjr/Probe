"""Evidence items and plans persistence models."""
from datetime import datetime
from sqlalchemy import String, Float, DateTime, Text, JSON, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from ..base import Base


class EvidencePlanModel(Base):
    """The targeted capabilities plan mapped during planning steps."""
    
    __tablename__ = "evidence_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    investigation_id: Mapped[str] = mapped_column(String(100), ForeignKey("investigations.session_id", ondelete="CASCADE"), unique=True, index=True)
    goal: Mapped[str] = mapped_column(Text)
    capabilities_json: Mapped[dict] = mapped_column(JSON, default=dict) # CapabilityRequest list


class EvidenceItemModel(Base):
    """Aggregated evidence records generated across MCP and platform providers."""
    
    __tablename__ = "evidence_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    evidence_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    investigation_id: Mapped[str] = mapped_column(String(100), ForeignKey("investigations.session_id", ondelete="CASCADE"), index=True)
    
    source_provider: Mapped[str] = mapped_column(String(100), index=True) # e.g. "github", "mlflow", "knowledge"
    evidence_type: Mapped[str] = mapped_column(String(100), index=True) # e.g. "drift_stats", "runbook_reference"
    
    # Decoupled server metrics
    capability: Mapped[str] = mapped_column(String(100), default="unknown")
    server: Mapped[str] = mapped_column(String(100), default="unknown")
    tool: Mapped[str] = mapped_column(String(100), default="unknown")
    transport: Mapped[str] = mapped_column(String(100), default="unknown")
    
    summary: Mapped[str] = mapped_column(Text)
    raw_json: Mapped[dict] = mapped_column(JSON, default=dict) # JSONB
    confidence_weight: Mapped[float] = mapped_column(Float, default=1.0)
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
