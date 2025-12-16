"""
Workflows API - Query and manage workflows.

Endpoints:
- GET /api/v1/workflows - List all workflows with filtering
- GET /api/v1/workflows/stats - Get workflow statistics
- GET /api/v1/workflows/{workflow_id} - Get workflow details
- GET /api/v1/workflows/{workflow_id}/state - Get full workflow state
- DELETE /api/v1/workflows/{workflow_id} - Delete a workflow
- POST /api/v1/workflows/{workflow_id}/retry - Retry a failed workflow
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Workflow, Invoice, Checkpoint, AuditLog
from app.schemas.workflow import (
    WorkflowResponse,
    WorkflowDetailResponse,
    WorkflowListResponse,
    WorkflowStateResponse,
)
from app.config import WorkflowStatus
from app.utils.logger import logger
from app.utils.helpers import utc_now_iso


router = APIRouter()


# ============================================
# LIST WORKFLOWS
# ============================================

@router.get(
    "",
    response_model=WorkflowListResponse,
    summary="List Workflows",
    description="""
Get a paginated list of all workflows with optional filtering.

**Filters:**
- `status`: Filter by workflow status (PENDING, RUNNING, PAUSED, COMPLETED, FAILED, MANUAL_HANDOFF)
- `invoice_id`: Filter by invoice ID (partial match)
- `vendor`: Filter by vendor name (partial match)

**Sorting:**
- Results are sorted by creation date (newest first)
    """,
)
async def list_workflows(
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[str] = Query(
        None, 
        alias="status", 
        description="Filter by workflow status"
    ),
    invoice_id: Optional[str] = Query(
        None,
        description="Filter by invoice ID (partial match)"
    ),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
) -> WorkflowListResponse:
    """
    List all workflows with pagination and filtering.
    
    Args:
        db: Database session
        status_filter: Optional status filter
        invoice_id: Optional invoice ID filter
        limit: Number of items per page
        offset: Pagination offset
        
    Returns:
        Paginated list of workflows
    """
    # Build base query
    query = select(Workflow).order_by(desc(Workflow.created_at))
    count_query = select(func.count(Workflow.id))
    
    # Apply filters
    filters = []
    
    if status_filter:
        filters.append(Workflow.status == status_filter.upper())
    
    if invoice_id:
        filters.append(Workflow.invoice_id.ilike(f"%{invoice_id}%"))
    
    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get paginated results
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    workflows = result.scalars().all()
    
    return WorkflowListResponse(
        items=[WorkflowResponse.model_validate(w.to_dict()) for w in workflows],
        total=total,
        limit=limit,
        offset=offset,
    )


# ============================================
# WORKFLOW STATISTICS
# ============================================

@router.get(
    "/stats",
    response_model=dict[str, Any],
    summary="Get Workflow Statistics",
    description="Get summary statistics of all workflows grouped by status.",
)
async def get_workflow_stats(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get workflow statistics.
    
    Returns:
        Workflow counts by status and other aggregate metrics
    """
    # Count by status
    status_counts = {}
    for status_value in [
        WorkflowStatus.PENDING,
        WorkflowStatus.RUNNING,
        WorkflowStatus.PAUSED,
        WorkflowStatus.COMPLETED,
        WorkflowStatus.FAILED,
        WorkflowStatus.MANUAL_HANDOFF,
    ]:
        count_query = select(func.count(Workflow.id)).where(Workflow.status == status_value)
        result = await db.execute(count_query)
        status_counts[status_value.lower()] = result.scalar() or 0
    
    # Total count
    total_query = select(func.count(Workflow.id))
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    # Average match score for completed workflows
    avg_score_query = select(func.avg(Workflow.match_score)).where(
        and_(
            Workflow.status == WorkflowStatus.COMPLETED,
            Workflow.match_score.isnot(None)
        )
    )
    avg_score_result = await db.execute(avg_score_query)
    avg_match_score = avg_score_result.scalar()
    
    # Recent activity (last 24 hours)
    from datetime import timedelta
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_query = select(func.count(Workflow.id)).where(Workflow.created_at >= yesterday)
    recent_result = await db.execute(recent_query)
    recent_count = recent_result.scalar() or 0
    
    return {
        "total": total,
        "by_status": status_counts,
        "pending_review": status_counts.get("paused", 0),
        "success_rate": round(
            status_counts.get("completed", 0) / max(total, 1) * 100, 2
        ),
        "average_match_score": round(avg_match_score, 3) if avg_match_score else None,
        "last_24_hours": recent_count,
        "timestamp": utc_now_iso(),
    }


# ============================================
# GET WORKFLOW DETAILS
# ============================================

@router.get(
    "/{workflow_id}",
    response_model=WorkflowDetailResponse,
    summary="Get Workflow Details",
    description="""
Get detailed information about a specific workflow.

Includes:
- Workflow metadata and status
- Associated invoice data
- Checkpoints (if any)
- Match results
    """,
    responses={
        404: {"description": "Workflow not found"}
    }
)
async def get_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
) -> WorkflowDetailResponse:
    """
    Get workflow details by ID.
    
    Args:
        workflow_id: Workflow identifier
        db: Database session
        
    Returns:
        Detailed workflow information
    """
    # Query workflow
    query = select(Workflow).where(Workflow.workflow_id == workflow_id)
    result = await db.execute(query)
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Workflow not found",
                "workflow_id": workflow_id,
                "timestamp": utc_now_iso(),
            },
        )
    
    # Get invoice details
    invoice_data = None
    if workflow.invoice:
        invoice_data = workflow.invoice.to_dict()
    
    # Get checkpoints
    checkpoints_data = [cp.to_dict() for cp in workflow.checkpoints]
    
    return WorkflowDetailResponse(
        **workflow.to_dict(),
        invoice=invoice_data,
        checkpoints=checkpoints_data,
    )


# ============================================
# GET WORKFLOW STATE
# ============================================

@router.get(
    "/{workflow_id}/state",
    response_model=WorkflowStateResponse,
    summary="Get Workflow State",
    description="""
Get the full accumulated state of a workflow.

This includes all data generated by each stage:
- Parsed invoice data
- Vendor profile
- Match evidence
- Accounting entries
- And more...
    """,
)
async def get_workflow_state(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
) -> WorkflowStateResponse:
    """
    Get full workflow state including all stage outputs.
    
    Args:
        workflow_id: Workflow identifier
        db: Database session
        
    Returns:
        Full workflow state data
    """
    # Query workflow
    query = select(Workflow).where(Workflow.workflow_id == workflow_id)
    result = await db.execute(query)
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow not found: {workflow_id}",
        )
    
    return WorkflowStateResponse(
        workflow_id=workflow.workflow_id,
        status=workflow.status,
        current_stage=workflow.current_stage,
        state_data=workflow.state_data or {},
    )


# ============================================
# GET WORKFLOW TIMELINE
# ============================================

@router.get(
    "/{workflow_id}/timeline",
    response_model=dict[str, Any],
    summary="Get Workflow Timeline",
    description="Get a chronological timeline of workflow events.",
)
async def get_workflow_timeline(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get workflow execution timeline from audit logs.
    
    Args:
        workflow_id: Workflow identifier
        db: Database session
        
    Returns:
        Timeline of workflow events
    """
    # Verify workflow exists
    workflow_query = select(Workflow).where(Workflow.workflow_id == workflow_id)
    workflow_result = await db.execute(workflow_query)
    workflow = workflow_result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow not found: {workflow_id}",
        )
    
    # Get audit logs
    logs_query = (
        select(AuditLog)
        .where(AuditLog.workflow_id == workflow_id)
        .order_by(AuditLog.created_at)
    )
    logs_result = await db.execute(logs_query)
    logs = logs_result.scalars().all()
    
    timeline = []
    for log in logs:
        timeline.append({
            "timestamp": log.created_at.isoformat() if log.created_at else None,
            "event_type": log.event_type,
            "stage_id": log.stage_id,
            "message": log.message,
            "actor_type": log.actor_type,
            "actor_id": log.actor_id,
        })
    
    return {
        "workflow_id": workflow_id,
        "status": workflow.status,
        "events_count": len(timeline),
        "timeline": timeline,
    }


# ============================================
# DELETE WORKFLOW
# ============================================

@router.delete(
    "/{workflow_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Workflow",
    description="""
Delete a workflow and all associated data.

**Warning:** This action is irreversible. All related data will be deleted:
- Workflow record
- Checkpoints
- Human reviews
- Audit logs
    """,
    responses={
        204: {"description": "Workflow deleted successfully"},
        404: {"description": "Workflow not found"},
    }
)
async def delete_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a workflow and all associated data.
    
    Args:
        workflow_id: Workflow identifier
        db: Database session
    """
    # Query workflow
    query = select(Workflow).where(Workflow.workflow_id == workflow_id)
    result = await db.execute(query)
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow not found: {workflow_id}",
        )
    
    # Delete workflow (cascades to checkpoints, audit logs)
    await db.delete(workflow)
    await db.commit()
    
    logger.info(f"🗑️ Deleted workflow: {workflow_id}")


# ============================================
# RETRY WORKFLOW
# ============================================

@router.post(
    "/{workflow_id}/retry",
    response_model=dict[str, Any],
    summary="Retry Failed Workflow",
    description="""
Retry a failed workflow from the beginning.

Only workflows with status FAILED can be retried.
    """,
    responses={
        200: {"description": "Workflow retry started"},
        400: {"description": "Workflow cannot be retried"},
        404: {"description": "Workflow not found"},
    }
)
async def retry_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Retry a failed workflow.
    
    Args:
        workflow_id: Workflow identifier
        db: Database session
        
    Returns:
        New workflow ID for the retry
    """
    # Query workflow
    query = select(Workflow).where(Workflow.workflow_id == workflow_id)
    result = await db.execute(query)
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow not found: {workflow_id}",
        )
    
    if workflow.status != WorkflowStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only FAILED workflows can be retried. Current status: {workflow.status}",
        )
    
    # Get original invoice payload
    raw_payload = workflow.state_data.get("raw_payload", {})
    if not raw_payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot retry: original invoice payload not found",
        )
    
    # Create new workflow with incremented retry count
    from app.schemas.invoice import InvoicePayload
    from app.services.workflow_service import WorkflowService
    
    payload = InvoicePayload(**raw_payload)
    workflow_service = WorkflowService(db)
    
    # Update original workflow
    workflow.retry_count += 1
    
    # Start new workflow
    new_result = await workflow_service.start_workflow(payload)
    
    logger.info(f"🔄 Retrying workflow {workflow_id} as {new_result.workflow_id}")
    
    return {
        "success": True,
        "original_workflow_id": workflow_id,
        "new_workflow_id": new_result.workflow_id,
        "retry_count": workflow.retry_count,
        "timestamp": utc_now_iso(),
    }


# ============================================
# CANCEL WORKFLOW
# ============================================

@router.post(
    "/{workflow_id}/cancel",
    response_model=dict[str, Any],
    summary="Cancel Running Workflow",
    description="Cancel a workflow that is currently running or paused.",
)
async def cancel_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Cancel a running or paused workflow.
    
    Args:
        workflow_id: Workflow identifier
        db: Database session
        
    Returns:
        Cancellation confirmation
    """
    # Query workflow
    query = select(Workflow).where(Workflow.workflow_id == workflow_id)
    result = await db.execute(query)
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow not found: {workflow_id}",
        )
    
    if workflow.status not in [WorkflowStatus.RUNNING, WorkflowStatus.PAUSED, WorkflowStatus.PENDING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel workflow with status: {workflow.status}",
        )
    
    # Update workflow status
    previous_status = workflow.status
    workflow.status = WorkflowStatus.FAILED
    workflow.error_message = "Cancelled by user"
    workflow.completed_at = datetime.utcnow()
    
    # Add audit log
    audit_log = AuditLog(
        workflow_db_id=workflow.id,
        workflow_id=workflow_id,
        event_type="workflow_cancelled",
        message=f"Workflow cancelled. Previous status: {previous_status}",
        actor_type="user",
    )
    db.add(audit_log)
    await db.commit()
    
    logger.info(f"🛑 Cancelled workflow: {workflow_id}")
    
    return {
        "success": True,
        "workflow_id": workflow_id,
        "previous_status": previous_status,
        "new_status": WorkflowStatus.FAILED,
        "timestamp": utc_now_iso(),
    }
