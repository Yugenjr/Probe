"""Knowledge reference and long term incident memory models."""
from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from ..base import Base


class KnowledgeReference(Base):
    """Citational logging of document references and runbooks accessed during reasoning."""
    
    __tablename__ = "knowledge_references"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    investigation_id: Mapped[str] = mapped_column(String(100), ForeignKey("investigations.session_id", ondelete="CASCADE"), index=True)
    document_id: Mapped[str] = mapped_column(String(100), index=True)
    document_type: Mapped[str] = mapped_column(String(50)) # e.g. "runbook", "kb_article", "historical_session"
    title: Mapped[str] = mapped_column(String(200))
    usage_count: Mapped[int] = mapped_column(Integer, default=1)
    referenced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class InvestigationMemory(Base):
    """Long-term resolved memory index for quick lookup of similar incidents."""
    
    __tablename__ = "investigation_memory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    investigation_id: Mapped[str] = mapped_column(String(100), ForeignKey("investigations.session_id", ondelete="CASCADE"), unique=True, index=True)
    model_id: Mapped[str] = mapped_column(String(100), index=True)
    
    problem_signature: Mapped[str] = mapped_column(Text)
    resolution: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    
    evidence_ids: Mapped[dict] = mapped_column(JSON, default=list) # List[str]
    runbooks_used: Mapped[dict] = mapped_column(JSON, default=list) # List[str]
    git_commit_hash: Mapped[str] = mapped_column(String(100), default="N/A")
    mlflow_run_id: Mapped[str] = mapped_column(String(100), default="N/A")
    outcome: Mapped[str] = mapped_column(String(100), default="resolved")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
