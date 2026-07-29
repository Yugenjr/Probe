"""Report models, hypotheses and evaluations persistence."""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from ..base import Base


class HypothesisModel(Base):
    """Synthesized root-cause theories formulated from universal evidence."""
    
    __tablename__ = "hypotheses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hypothesis_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    investigation_id: Mapped[str] = mapped_column(String(100), ForeignKey("investigations.session_id", ondelete="CASCADE"), index=True)
    
    title: Mapped[str] = mapped_column(String(200))
    detailed_reasoning: Mapped[str] = mapped_column(Text)
    supporting_evidence_ids: Mapped[dict] = mapped_column(JSON, default=list) # List[str]
    likelihood_score: Mapped[float] = mapped_column(Float, default=0.0)
    verified_by_simulation: Mapped[bool] = mapped_column(Boolean, default=False)
    weaknesses: Mapped[dict] = mapped_column(JSON, default=list) # List[str]
    ranking: Mapped[int] = mapped_column(Integer, default=1)


class EvaluationModel(Base):
    """Evaluator decisions appraising hypotheses and choosing remediation paths."""
    
    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    investigation_id: Mapped[str] = mapped_column(String(100), ForeignKey("investigations.session_id", ondelete="CASCADE"), unique=True, index=True)
    best_hypothesis_id: Mapped[str] = mapped_column(String(100), index=True)
    recommended_actions_json: Mapped[dict] = mapped_column(JSON, default=list) # List[Dict]
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ReportModel(Base):
    """Forensic report compiling executive summary and analytical details."""
    
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    report_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    investigation_id: Mapped[str] = mapped_column(String(100), ForeignKey("investigations.session_id", ondelete="CASCADE"), unique=True, index=True)
    
    primary_root_cause: Mapped[str] = mapped_column(String(200))
    markdown_content: Mapped[str] = mapped_column(Text)
    html_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    json_content: Mapped[dict] = mapped_column(JSON, default=dict)
    
    generation_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    report_version: Mapped[str] = mapped_column(String(50), default="1.0.0")
