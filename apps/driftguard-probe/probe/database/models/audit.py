"""System compliance and security audit logs."""
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from ..base import Base


class AuditLog(Base):
    """Compliance log tracking administrative and lifecycle events of investigations."""
    
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    investigation_id: Mapped[str] = mapped_column(String(100), index=True)
    event_name: Mapped[str] = mapped_column(String(100), index=True) # e.g. "InvestigationStarted", "Closed"
    actor: Mapped[str] = mapped_column(String(100), default="probe-system")
    details: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
