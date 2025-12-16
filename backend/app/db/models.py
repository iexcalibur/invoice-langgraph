"""SQLAlchemy database models for Invoice LangGraph Agent."""

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Invoice(Base):
    """Invoice model - stores raw invoice data."""
    
    __tablename__ = "invoices"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    vendor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    vendor_tax_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    invoice_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    due_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    line_items: Mapped[dict[str, Any]] = mapped_column(JSON, default=list)
    attachments: Mapped[list[str]] = mapped_column(JSON, default=list)
    raw_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    workflows: Mapped[list["Workflow"]] = relationship("Workflow", back_populates="invoice", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<Invoice(id={self.invoice_id}, vendor={self.vendor_name}, amount={self.amount})>"
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "invoice_id": self.invoice_id, "vendor_name": self.vendor_name,
            "vendor_tax_id": self.vendor_tax_id, "invoice_date": self.invoice_date,
            "due_date": self.due_date, "amount": self.amount, "currency": self.currency,
            "line_items": self.line_items, "attachments": self.attachments,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Workflow(Base):
    """Workflow model - tracks workflow execution state."""
    
    __tablename__ = "workflows"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workflow_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    invoice_db_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("invoices.id", ondelete="SET NULL"), nullable=True)
    invoice_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True)
    current_stage: Mapped[str | None] = mapped_column(String(50), nullable=True)
    state_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    match_result: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="workflows", lazy="selectin")
    checkpoints: Mapped[list["Checkpoint"]] = relationship("Checkpoint", back_populates="workflow", lazy="selectin")
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="workflow", lazy="selectin")
    
    __table_args__ = (Index("ix_workflows_status_created", "status", "created_at"),)
    
    def __repr__(self) -> str:
        return f"<Workflow(id={self.workflow_id}, status={self.status}, stage={self.current_stage})>"
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "workflow_id": self.workflow_id, "invoice_id": self.invoice_id,
            "status": self.status, "current_stage": self.current_stage,
            "match_score": self.match_score, "match_result": self.match_result,
            "error_message": self.error_message, "retry_count": self.retry_count,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def to_detailed_dict(self) -> dict[str, Any]:
        result = self.to_dict()
        result["state_data"] = self.state_data
        return result


class Checkpoint(Base):
    """Checkpoint model - stores HITL checkpoint data."""
    
    __tablename__ = "checkpoints"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    checkpoint_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    workflow_db_id: Mapped[int] = mapped_column(Integer, ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    workflow_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    stage_id: Mapped[str] = mapped_column(String(50), nullable=False)
    state_blob: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    paused_reason: Mapped[str] = mapped_column(Text, nullable=False)
    review_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolution: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resolver_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    resolver_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    
    workflow: Mapped["Workflow"] = relationship("Workflow", back_populates="checkpoints", lazy="selectin")
    human_review: Mapped["HumanReview | None"] = relationship("HumanReview", back_populates="checkpoint", uselist=False, lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<Checkpoint(id={self.checkpoint_id}, stage={self.stage_id}, resolved={self.is_resolved})>"
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "checkpoint_id": self.checkpoint_id, "workflow_id": self.workflow_id,
            "stage_id": self.stage_id, "paused_reason": self.paused_reason, "review_url": self.review_url,
            "is_resolved": self.is_resolved, "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolution": self.resolution, "resolver_id": self.resolver_id, "resolver_notes": self.resolver_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class HumanReview(Base):
    """Human Review model - queue entries for human review."""
    
    __tablename__ = "human_reviews"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    checkpoint_db_id: Mapped[int] = mapped_column(Integer, ForeignKey("checkpoints.id", ondelete="CASCADE"), nullable=False)
    checkpoint_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    invoice_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    vendor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    reason_for_hold: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    review_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    
    checkpoint: Mapped["Checkpoint"] = relationship("Checkpoint", back_populates="human_review", lazy="selectin")
    
    __table_args__ = (Index("ix_human_reviews_status_priority", "status", "priority"),)
    
    def __repr__(self) -> str:
        return f"<HumanReview(invoice={self.invoice_id}, status={self.status})>"
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id, "invoice_id": self.invoice_id, "vendor_name": self.vendor_name,
            "amount": self.amount, "currency": self.currency, "match_score": self.match_score,
            "reason_for_hold": self.reason_for_hold, "status": self.status, "priority": self.priority,
            "review_url": self.review_url, "assigned_to": self.assigned_to,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


class AuditLog(Base):
    """Audit Log model - tracks all operations."""
    
    __tablename__ = "audit_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workflow_db_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("workflows.id", ondelete="SET NULL"), nullable=True)
    workflow_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    stage_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    actor_type: Mapped[str] = mapped_column(String(50), default="system")
    actor_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, index=True)
    
    workflow: Mapped["Workflow | None"] = relationship("Workflow", back_populates="audit_logs", lazy="selectin")
    
    __table_args__ = (Index("ix_audit_logs_workflow_event", "workflow_id", "event_type"),)
    
    def __repr__(self) -> str:
        return f"<AuditLog(event={self.event_type}, workflow={self.workflow_id})>"
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "workflow_id": self.workflow_id, "event_type": self.event_type,
            "stage_id": self.stage_id, "message": self.message, "details": self.details,
            "actor_type": self.actor_type, "actor_id": self.actor_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


__all__ = ["Invoice", "Workflow", "Checkpoint", "HumanReview", "AuditLog"]
