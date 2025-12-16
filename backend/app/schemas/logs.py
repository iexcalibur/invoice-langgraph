"""Log-related Pydantic schemas."""

from typing import Any

from pydantic import BaseModel, Field


class LogEntry(BaseModel):
    """Single log entry."""
    
    timestamp: str
    level: str
    stage_id: str | None = None
    event_type: str
    message: str
    details: dict[str, Any] | None = None


class StageLog(BaseModel):
    """Logs for a specific stage."""
    
    stage_id: str
    status: str
    started_at: str | None
    completed_at: str | None
    duration_ms: float | None
    entries: list[LogEntry] = Field(default_factory=list)
    outputs: dict[str, Any] = Field(default_factory=dict)


class WorkflowLogsResponse(BaseModel):
    """Complete workflow logs response."""
    
    workflow_id: str
    status: str
    stages: list[StageLog] = Field(default_factory=list)
    bigtool_selections: list[dict[str, Any]] = Field(default_factory=list)
    mcp_calls: list[dict[str, Any]] = Field(default_factory=list)
