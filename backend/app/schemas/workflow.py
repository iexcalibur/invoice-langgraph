"""Workflow-related Pydantic schemas."""

from typing import Any

from pydantic import BaseModel, Field


class WorkflowResponse(BaseModel):
    """Workflow summary response."""
    
    id: int
    workflow_id: str
    invoice_id: str
    status: str
    current_stage: str | None
    match_score: float | None
    match_result: str | None
    error_message: str | None
    retry_count: int
    started_at: str | None
    completed_at: str | None
    created_at: str | None
    updated_at: str | None
    
    model_config = {"from_attributes": True}


class WorkflowDetailResponse(WorkflowResponse):
    """Detailed workflow response with related data."""
    
    invoice: dict[str, Any] | None = None
    checkpoints: list[dict[str, Any]] = Field(default_factory=list)


class WorkflowListResponse(BaseModel):
    """Paginated list of workflows."""
    
    items: list[WorkflowResponse]
    total: int
    limit: int
    offset: int


class WorkflowStateResponse(BaseModel):
    """Full workflow state response."""
    
    workflow_id: str
    status: str
    current_stage: str | None
    state_data: dict[str, Any]
