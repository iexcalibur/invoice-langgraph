"""Human review Pydantic schemas."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class HumanReviewItem(BaseModel):
    """Human review queue item."""
    
    checkpoint_id: str
    invoice_id: str
    vendor_name: str
    amount: float
    currency: str = "USD"
    match_score: float | None
    reason_for_hold: str
    status: str
    priority: int
    review_url: str | None
    assigned_to: str | None
    created_at: str | None
    expires_at: str | None
    
    model_config = {"from_attributes": True}


class HumanReviewListResponse(BaseModel):
    """Paginated list of human reviews."""
    
    items: list[HumanReviewItem]
    total: int
    limit: int
    offset: int


class HumanReviewDetailResponse(HumanReviewItem):
    """Detailed human review response."""
    
    checkpoint_data: dict[str, Any] = Field(default_factory=dict)
    workflow_status: str | None = None
    invoice_data: dict[str, Any] = Field(default_factory=dict)
    matched_pos: list[dict[str, Any]] = Field(default_factory=list)
    match_evidence: dict[str, Any] = Field(default_factory=dict)


class HumanDecisionRequest(BaseModel):
    """Human review decision request."""
    
    checkpoint_id: str = Field(..., description="Checkpoint ID to resolve")
    decision: Literal["ACCEPT", "REJECT"] = Field(..., description="Review decision")
    notes: str = Field("", description="Reviewer notes")
    reviewer_id: str = Field(..., description="Reviewer identifier")
    
    model_config = {"json_schema_extra": {
        "example": {
            "checkpoint_id": "cp_wf_INV-001_abc123",
            "decision": "ACCEPT",
            "notes": "Approved after vendor confirmation",
            "reviewer_id": "user_123"
        }
    }}


class HumanDecisionResponse(BaseModel):
    """Human review decision response."""
    
    success: bool
    checkpoint_id: str
    decision: str
    resume_token: str | None = None
    next_stage: str | None = None
    workflow_status: str | None = None
