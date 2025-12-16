"""
Invoke API - Start invoice processing workflow.

Endpoints:
- POST /api/v1/invoke - Start async workflow processing
- POST /api/v1/invoke/sync - Start and wait for completion
- POST /api/v1/invoke/validate - Validate invoice payload without processing
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import Invoice, Workflow, AuditLog
from app.schemas.invoice import InvoicePayload, InvokeResponse
from app.services.workflow_service import WorkflowService
from app.config import WorkflowStatus, StageID
from app.utils.helpers import generate_workflow_id, utc_now_iso
from app.utils.logger import logger


router = APIRouter()


# ============================================
# INVOKE ENDPOINTS
# ============================================

@router.post(
    "",
    response_model=InvokeResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start Invoice Processing",
    description="""
Start a new invoice processing workflow.

The workflow will:
1. Validate the invoice payload
2. Process through 12 stages (INTAKE → COMPLETE)
3. Pause at CHECKPOINT_HITL if matching fails
4. Return workflow ID for status tracking

**Note:** Processing happens asynchronously. Use the returned `workflow_id` 
to track progress via `/workflows/{workflow_id}` endpoint.
    """,
    responses={
        202: {
            "description": "Workflow started successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "workflow_id": "wf_INV-2024-001_abc12345",
                        "invoice_id": "INV-2024-001",
                        "status": "RUNNING",
                        "current_stage": "INTAKE",
                        "message": "Workflow started successfully",
                        "timestamp": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def invoke_workflow(
    payload: InvoicePayload,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> InvokeResponse:
    """
    Start a new invoice processing workflow.
    
    Args:
        payload: Invoice data to process
        request: FastAPI request object
        background_tasks: Background task manager
        db: Database session
        
    Returns:
        InvokeResponse with workflow ID and initial status
    """
    logger.info(f"📥 Received invoice: {payload.invoice_id}")
    logger.debug(f"Invoice payload: vendor={payload.vendor_name}, amount={payload.amount}")
    
    try:
        # Initialize workflow service
        workflow_service = WorkflowService(db)
        
        # Start workflow (async processing)
        result = await workflow_service.start_workflow(payload)
        
        logger.info(f"✅ Workflow started: {result.workflow_id}")
        
        return result
        
    except ValueError as e:
        # Validation errors
        logger.warning(f"⚠️ Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "Validation error",
                "message": str(e),
                "timestamp": utc_now_iso(),
            },
        )
    except Exception as e:
        # Unexpected errors
        logger.error(f"❌ Failed to start workflow: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to start workflow",
                "message": str(e),
                "timestamp": utc_now_iso(),
            },
        )


@router.post(
    "/sync",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Start Invoice Processing (Synchronous)",
    description="""
Start a new invoice processing workflow and wait for completion.

**Warning:** This endpoint blocks until the workflow completes or pauses for HITL.
Use the async `/invoke` endpoint for production workloads.

**Use cases:**
- Testing and debugging
- Small batch processing
- Demo scenarios
    """,
    responses={
        200: {
            "description": "Workflow completed or paused",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "workflow_id": "wf_INV-2024-001_abc12345",
                        "status": "COMPLETED",
                        "current_stage": "COMPLETE",
                        "result": {"final_payload": {}},
                        "timestamp": "2024-01-15T10:30:05Z"
                    }
                }
            }
        }
    }
)
async def invoke_workflow_sync(
    payload: InvoicePayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Start workflow and wait for completion (synchronous).
    
    This endpoint blocks until the workflow either:
    - Completes successfully
    - Fails with an error
    - Pauses for human review (HITL)
    
    Args:
        payload: Invoice data to process
        request: FastAPI request object
        db: Database session
        
    Returns:
        Complete workflow result including final state
    """
    logger.info(f"📥 Received invoice (sync): {payload.invoice_id}")
    
    try:
        # Initialize workflow service
        workflow_service = WorkflowService(db)
        
        # Start and wait for completion
        result = await workflow_service.start_workflow_sync(payload)
        
        logger.info(f"✅ Workflow completed: {result.get('workflow_id')} - {result.get('status')}")
        
        return {
            "success": True,
            "workflow_id": result.get("workflow_id"),
            "invoice_id": payload.invoice_id,
            "status": result.get("status"),
            "current_stage": result.get("current_stage"),
            "match_score": result.get("match_score"),
            "match_result": result.get("match_result"),
            "checkpoint_id": result.get("checkpoint_id"),
            "review_url": result.get("review_url"),
            "result": result,
            "timestamp": utc_now_iso(),
        }
        
    except ValueError as e:
        logger.warning(f"⚠️ Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "Validation error", "message": str(e)},
        )
    except Exception as e:
        logger.error(f"❌ Workflow failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Workflow execution failed", "message": str(e)},
        )


@router.post(
    "/validate",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Validate Invoice Payload",
    description="""
Validate an invoice payload without starting a workflow.

Use this endpoint to:
- Pre-validate invoices before submission
- Check for missing required fields
- Verify data format
    """,
)
async def validate_invoice(
    payload: InvoicePayload,
) -> dict[str, Any]:
    """
    Validate invoice payload without processing.
    
    Args:
        payload: Invoice data to validate
        
    Returns:
        Validation result with any warnings
    """
    warnings = []
    
    # Check for optional but recommended fields
    if not payload.vendor_tax_id:
        warnings.append("vendor_tax_id is missing - may affect vendor enrichment")
    
    if not payload.invoice_date:
        warnings.append("invoice_date is missing - will use current date")
    
    if not payload.due_date:
        warnings.append("due_date is missing - payment scheduling may be affected")
    
    if not payload.line_items:
        warnings.append("line_items is empty - detailed reconciliation not possible")
    
    if not payload.attachments:
        warnings.append("attachments is empty - OCR will use payload data only")
    
    # Validate line item totals
    if payload.line_items:
        line_total = sum(item.total for item in payload.line_items)
        if abs(line_total - payload.amount) > 0.01:
            warnings.append(
                f"Line items total ({line_total}) does not match invoice amount ({payload.amount})"
            )
    
    return {
        "valid": True,
        "invoice_id": payload.invoice_id,
        "warnings": warnings,
        "warning_count": len(warnings),
        "timestamp": utc_now_iso(),
    }


@router.post(
    "/batch",
    response_model=dict[str, Any],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start Batch Invoice Processing",
    description="""
Start processing multiple invoices in batch.

**Note:** Each invoice is processed independently. Failed invoices 
do not affect others in the batch.
    """,
)
async def invoke_batch(
    payloads: list[InvoicePayload],
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Start batch invoice processing.
    
    Args:
        payloads: List of invoice payloads
        request: FastAPI request object
        db: Database session
        
    Returns:
        Batch processing status with workflow IDs
    """
    if len(payloads) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum batch size is 50 invoices",
        )
    
    logger.info(f"📥 Received batch of {len(payloads)} invoices")
    
    results = []
    workflow_service = WorkflowService(db)
    
    for payload in payloads:
        try:
            result = await workflow_service.start_workflow(payload)
            results.append({
                "invoice_id": payload.invoice_id,
                "workflow_id": result.workflow_id,
                "status": "started",
                "error": None,
            })
        except Exception as e:
            results.append({
                "invoice_id": payload.invoice_id,
                "workflow_id": None,
                "status": "failed",
                "error": str(e),
            })
    
    started = sum(1 for r in results if r["status"] == "started")
    failed = sum(1 for r in results if r["status"] == "failed")
    
    return {
        "success": True,
        "total": len(payloads),
        "started": started,
        "failed": failed,
        "results": results,
        "timestamp": utc_now_iso(),
    }
