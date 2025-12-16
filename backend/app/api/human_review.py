"""
Human Review API - HITL (Human-in-the-Loop) endpoints.

Endpoints:
- GET /api/v1/human-review/pending - List pending reviews
- GET /api/v1/human-review/stats - Get review statistics
- GET /api/v1/human-review/{checkpoint_id} - Get review details
- POST /api/v1/human-review/decision - Submit review decision
- POST /api/v1/human-review/{checkpoint_id}/assign - Assign review to user
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import HumanReview, Checkpoint, Workflow, AuditLog
from app.schemas.human_review import (
    HumanReviewItem,
    HumanReviewListResponse,
    HumanReviewDetailResponse,
    HumanDecisionRequest,
    HumanDecisionResponse,
)
from app.services.review_service import ReviewService
from app.config import HumanDecisionType
from app.utils.logger import logger
from app.utils.helpers import utc_now_iso


router = APIRouter()


# ============================================
# LIST PENDING REVIEWS
# ============================================

@router.get(
    "/pending",
    response_model=HumanReviewListResponse,
    summary="List Pending Reviews",
    description="""
Get all invoices pending human review.

This endpoint matches the API contract defined in workflow.json:
```json
{
  "path": "/human-review/pending",
  "method": "GET"
}
```

**Sorting:**
- Results are sorted by priority (highest first), then by creation date (oldest first)

**Use cases:**
- Populate the Human Review queue in the UI
- Monitor pending review backlog
    """,
)
async def list_pending_reviews(
    db: AsyncSession = Depends(get_db),
    priority: Optional[int] = Query(None, description="Filter by minimum priority"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned reviewer"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
) -> HumanReviewListResponse:
    """
    List all pending human reviews.
    
    Args:
        db: Database session
        priority: Minimum priority filter
        assigned_to: Filter by assigned reviewer
        limit: Number of items per page
        offset: Pagination offset
        
    Returns:
        Paginated list of pending review items
    """
    # Build query - pending reviews ordered by priority and creation time
    query = (
        select(HumanReview)
        .where(HumanReview.status == "PENDING")
        .order_by(desc(HumanReview.priority), HumanReview.created_at)
    )
    count_query = select(func.count(HumanReview.id)).where(HumanReview.status == "PENDING")
    
    # Apply filters
    filters = [HumanReview.status == "PENDING"]
    
    if priority is not None:
        filters.append(HumanReview.priority >= priority)
    
    if assigned_to:
        filters.append(HumanReview.assigned_to == assigned_to)
    
    if len(filters) > 1:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get paginated results
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    reviews = result.scalars().all()
    
    return HumanReviewListResponse(
        items=[HumanReviewItem.model_validate(r.to_dict()) for r in reviews],
        total=total,
        limit=limit,
        offset=offset,
    )


# ============================================
# REVIEW STATISTICS
# ============================================

@router.get(
    "/stats",
    response_model=dict[str, Any],
    summary="Get Review Statistics",
    description="Get summary statistics of human reviews.",
)
async def get_review_stats(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get human review statistics.
    
    Returns:
        Review counts by status and other metrics
    """
    # Count by status
    status_counts = {}
    for status_value in ["PENDING", "REVIEWED", "EXPIRED"]:
        count_query = select(func.count(HumanReview.id)).where(
            HumanReview.status == status_value
        )
        result = await db.execute(count_query)
        status_counts[status_value.lower()] = result.scalar() or 0
    
    # Average time to review (for reviewed items)
    # This would require additional tracking in production
    
    # High priority pending count
    high_priority_query = select(func.count(HumanReview.id)).where(
        and_(
            HumanReview.status == "PENDING",
            HumanReview.priority >= 5
        )
    )
    high_priority_result = await db.execute(high_priority_query)
    high_priority_count = high_priority_result.scalar() or 0
    
    # Total amount pending review
    amount_query = select(func.sum(HumanReview.amount)).where(
        HumanReview.status == "PENDING"
    )
    amount_result = await db.execute(amount_query)
    total_amount_pending = amount_result.scalar() or 0
    
    return {
        "total": sum(status_counts.values()),
        "by_status": status_counts,
        "pending": status_counts.get("pending", 0),
        "high_priority_pending": high_priority_count,
        "total_amount_pending": round(total_amount_pending, 2),
        "timestamp": utc_now_iso(),
    }


# ============================================
# GET REVIEW DETAILS
# ============================================

@router.get(
    "/{checkpoint_id}",
    response_model=HumanReviewDetailResponse,
    summary="Get Review Details",
    description="""
Get detailed information for a specific review.

Includes:
- Invoice summary
- Match details and evidence
- PO comparison data
- Checkpoint state
    """,
    responses={
        404: {"description": "Review not found"}
    }
)
async def get_review_detail(
    checkpoint_id: str,
    db: AsyncSession = Depends(get_db),
) -> HumanReviewDetailResponse:
    """
    Get detailed review information including invoice and match data.
    
    Args:
        checkpoint_id: Checkpoint identifier
        db: Database session
        
    Returns:
        Detailed review information
    """
    # Query review with checkpoint
    query = select(HumanReview).where(HumanReview.checkpoint_id == checkpoint_id)
    result = await db.execute(query)
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Review not found",
                "checkpoint_id": checkpoint_id,
                "timestamp": utc_now_iso(),
            },
        )
    
    # Get checkpoint for state data
    checkpoint = review.checkpoint
    workflow = checkpoint.workflow if checkpoint else None
    
    # Build response
    response_data = review.to_dict()
    response_data["checkpoint_data"] = checkpoint.state_blob if checkpoint else {}
    response_data["workflow_status"] = workflow.status if workflow else None
    
    # Get invoice and PO data from checkpoint state
    state_blob = checkpoint.state_blob if checkpoint else {}
    
    response_data["invoice_data"] = {
        "invoice_id": state_blob.get("invoice_id"),
        "invoice_text": state_blob.get("invoice_text", ""),
        "parsed_line_items": state_blob.get("parsed_line_items", []),
        "amount": state_blob.get("raw_payload", {}).get("amount"),
        "currency": state_blob.get("raw_payload", {}).get("currency", "USD"),
    }
    
    response_data["matched_pos"] = state_blob.get("matched_pos", [])
    response_data["match_evidence"] = state_blob.get("match_evidence", {})
    
    return HumanReviewDetailResponse(**response_data)


# ============================================
# SUBMIT DECISION
# ============================================

@router.post(
    "/decision",
    response_model=HumanDecisionResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit Review Decision",
    description="""
Submit a human review decision (ACCEPT or REJECT).

This endpoint matches the API contract defined in workflow.json:
```json
{
  "path": "/human-review/decision",
  "method": "POST",
  "request_schema": {
    "checkpoint_id": "string",
    "decision": "string",
    "notes": "string",
    "reviewer_id": "string"
  }
}
```

**Decision outcomes:**
- **ACCEPT**: Workflow resumes at RECONCILE stage
- **REJECT**: Workflow completes with MANUAL_HANDOFF status
    """,
    responses={
        200: {
            "description": "Decision processed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "checkpoint_id": "cp_wf_INV-001_xyz789",
                        "decision": "ACCEPT",
                        "resume_token": "wf_INV-001_abc123",
                        "next_stage": "RECONCILE",
                        "workflow_status": "RUNNING"
                    }
                }
            }
        },
        400: {"description": "Invalid request or checkpoint already resolved"},
        404: {"description": "Checkpoint not found"}
    }
)
async def submit_decision(
    request: HumanDecisionRequest,
    db: AsyncSession = Depends(get_db),
) -> HumanDecisionResponse:
    """
    Submit human review decision and resume workflow.
    
    Args:
        request: Decision request with checkpoint_id, decision, notes, reviewer_id
        db: Database session
        
    Returns:
        Response with resume_token and next_stage
    """
    logger.info(f"📝 Review decision received: {request.checkpoint_id} → {request.decision}")
    
    # Validate decision
    if request.decision not in [HumanDecisionType.ACCEPT, HumanDecisionType.REJECT]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid decision. Must be ACCEPT or REJECT, got: {request.decision}",
        )
    
    try:
        # Initialize review service
        review_service = ReviewService(db)
        
        # Process decision
        result = await review_service.process_decision(
            checkpoint_id=request.checkpoint_id,
            decision=request.decision,
            reviewer_id=request.reviewer_id,
            notes=request.notes or "",
        )
        
        logger.info(
            f"✅ Decision processed: {request.checkpoint_id} | "
            f"Decision: {request.decision} | "
            f"Next: {result.get('next_stage')}"
        )
        
        return HumanDecisionResponse(
            success=True,
            checkpoint_id=request.checkpoint_id,
            decision=request.decision,
            resume_token=result.get("resume_token"),
            next_stage=result.get("next_stage"),
            workflow_status=result.get("workflow_status"),
        )
        
    except ValueError as e:
        # Business logic errors (already resolved, not found, etc.)
        logger.warning(f"⚠️ Decision error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        # Unexpected errors
        logger.error(f"❌ Decision processing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process decision: {str(e)}",
        )


# ============================================
# ASSIGN REVIEW
# ============================================

@router.post(
    "/{checkpoint_id}/assign",
    response_model=dict[str, Any],
    summary="Assign Review to User",
    description="Assign a pending review to a specific reviewer.",
)
async def assign_review(
    checkpoint_id: str,
    assignee: str = Query(..., description="User ID to assign the review to"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Assign a review to a specific user.
    
    Args:
        checkpoint_id: Checkpoint identifier
        assignee: User ID to assign
        db: Database session
        
    Returns:
        Assignment confirmation
    """
    # Query review
    query = select(HumanReview).where(HumanReview.checkpoint_id == checkpoint_id)
    result = await db.execute(query)
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review not found: {checkpoint_id}",
        )
    
    if review.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot assign review with status: {review.status}",
        )
    
    # Update assignment
    previous_assignee = review.assigned_to
    review.assigned_to = assignee
    await db.commit()
    
    logger.info(f"📋 Review {checkpoint_id} assigned to {assignee}")
    
    return {
        "success": True,
        "checkpoint_id": checkpoint_id,
        "assigned_to": assignee,
        "previous_assignee": previous_assignee,
        "timestamp": utc_now_iso(),
    }


# ============================================
# SET REVIEW PRIORITY
# ============================================

@router.post(
    "/{checkpoint_id}/priority",
    response_model=dict[str, Any],
    summary="Set Review Priority",
    description="Update the priority of a pending review.",
)
async def set_review_priority(
    checkpoint_id: str,
    priority: int = Query(..., ge=0, le=10, description="Priority level (0-10)"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Set the priority of a review.
    
    Args:
        checkpoint_id: Checkpoint identifier
        priority: Priority level (0-10, higher = more urgent)
        db: Database session
        
    Returns:
        Update confirmation
    """
    # Query review
    query = select(HumanReview).where(HumanReview.checkpoint_id == checkpoint_id)
    result = await db.execute(query)
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review not found: {checkpoint_id}",
        )
    
    if review.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update priority for review with status: {review.status}",
        )
    
    # Update priority
    previous_priority = review.priority
    review.priority = priority
    await db.commit()
    
    return {
        "success": True,
        "checkpoint_id": checkpoint_id,
        "priority": priority,
        "previous_priority": previous_priority,
        "timestamp": utc_now_iso(),
    }


# ============================================
# EXPIRE STALE REVIEWS
# ============================================

@router.post(
    "/expire-stale",
    response_model=dict[str, Any],
    summary="Expire Stale Reviews",
    description="Mark reviews as expired if they exceed the configured time limit.",
)
async def expire_stale_reviews(
    hours: int = Query(72, ge=1, le=720, description="Hours after which reviews expire"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Expire reviews that have been pending too long.
    
    Args:
        hours: Number of hours after which to expire
        db: Database session
        
    Returns:
        Expiration summary
    """
    from datetime import timedelta
    
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    # Find stale reviews
    query = select(HumanReview).where(
        and_(
            HumanReview.status == "PENDING",
            HumanReview.created_at < cutoff
        )
    )
    result = await db.execute(query)
    stale_reviews = result.scalars().all()
    
    expired_count = 0
    for review in stale_reviews:
        review.status = "EXPIRED"
        expired_count += 1
        
        # Update associated workflow
        if review.checkpoint and review.checkpoint.workflow:
            review.checkpoint.workflow.status = "FAILED"
            review.checkpoint.workflow.error_message = f"Review expired after {hours} hours"
    
    await db.commit()
    
    if expired_count > 0:
        logger.warning(f"⏰ Expired {expired_count} stale reviews (>{hours} hours)")
    
    return {
        "success": True,
        "expired_count": expired_count,
        "hours_threshold": hours,
        "cutoff_time": cutoff.isoformat(),
        "timestamp": utc_now_iso(),
    }
