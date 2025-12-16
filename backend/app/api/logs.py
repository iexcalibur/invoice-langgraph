"""
Logs API - Real-time workflow logs via SSE.

Endpoints:
- GET /api/v1/logs/{workflow_id} - Get all logs for a workflow
- GET /api/v1/logs/{workflow_id}/stream - Stream real-time logs via SSE
- GET /api/v1/logs/{workflow_id}/stages - Get logs grouped by stage
- GET /api/v1/logs/{workflow_id}/bigtool - Get Bigtool selection logs
- GET /api/v1/logs/{workflow_id}/mcp - Get MCP call logs
"""

import asyncio
import json
from typing import Any, AsyncGenerator, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db, get_db_context
from app.db.models import Workflow, AuditLog
from app.schemas.logs import WorkflowLogsResponse, StageLog, LogEntry
from app.config import WorkflowStatus
from app.utils.logger import logger
from app.utils.helpers import utc_now_iso


router = APIRouter()


# ============================================
# GET WORKFLOW LOGS
# ============================================

@router.get(
    "/{workflow_id}",
    response_model=WorkflowLogsResponse,
    summary="Get Workflow Logs",
    description="""
Get all logs for a workflow.

Includes:
- Stage execution logs
- Bigtool selection history
- MCP call history
- Error logs
    """,
    responses={
        404: {"description": "Workflow not found"}
    }
)
async def get_workflow_logs(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    stage_id: Optional[str] = Query(None, description="Filter by stage ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum logs to return"),
) -> WorkflowLogsResponse:
    """
    Get all logs for a workflow.
    
    Args:
        workflow_id: Workflow identifier
        db: Database session
        event_type: Optional event type filter
        stage_id: Optional stage ID filter
        limit: Maximum number of logs
        
    Returns:
        Structured workflow logs
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
    
    # Build logs query
    logs_query = (
        select(AuditLog)
        .where(AuditLog.workflow_id == workflow_id)
        .order_by(AuditLog.created_at)
        .limit(limit)
    )
    
    # Apply filters
    filters = [AuditLog.workflow_id == workflow_id]
    
    if event_type:
        filters.append(AuditLog.event_type == event_type)
    
    if stage_id:
        filters.append(AuditLog.stage_id == stage_id)
    
    if len(filters) > 1:
        logs_query = logs_query.where(and_(*filters))
    
    logs_result = await db.execute(logs_query)
    audit_logs = logs_result.scalars().all()
    
    # Group logs by stage
    stages: dict[str, StageLog] = {}
    bigtool_selections = []
    mcp_calls = []
    
    for log in audit_logs:
        # Collect Bigtool selections
        if log.event_type == "bigtool_selection":
            bigtool_selections.append({
                "timestamp": log.created_at.isoformat() if log.created_at else None,
                "capability": log.details.get("capability") if log.details else None,
                "selected": log.details.get("selected") if log.details else None,
                "available": log.details.get("available") if log.details else [],
                **(log.details or {}),
            })
        
        # Collect MCP calls
        elif log.event_type == "mcp_call":
            mcp_calls.append({
                "timestamp": log.created_at.isoformat() if log.created_at else None,
                "server": log.details.get("server") if log.details else None,
                "ability": log.details.get("ability") if log.details else None,
                **(log.details or {}),
            })
        
        # Group by stage
        if log.stage_id:
            if log.stage_id not in stages:
                stages[log.stage_id] = StageLog(
                    stage_id=log.stage_id,
                    status="completed",
                    started_at=None,
                    completed_at=None,
                    duration_ms=None,
                    entries=[],
                    outputs={},
                )
            
            # Update stage timing
            if log.event_type == "stage_start":
                stages[log.stage_id].started_at = (
                    log.created_at.isoformat() if log.created_at else None
                )
                stages[log.stage_id].status = "running"
            elif log.event_type == "stage_complete":
                stages[log.stage_id].completed_at = (
                    log.created_at.isoformat() if log.created_at else None
                )
                stages[log.stage_id].status = "completed"
                if log.details and "duration_ms" in log.details:
                    stages[log.stage_id].duration_ms = log.details["duration_ms"]
            elif log.event_type == "stage_error":
                stages[log.stage_id].status = "failed"
            
            # Add log entry
            stages[log.stage_id].entries.append(
                LogEntry(
                    timestamp=log.created_at.isoformat() if log.created_at else "",
                    level="ERROR" if "error" in log.event_type.lower() else "INFO",
                    stage_id=log.stage_id,
                    event_type=log.event_type,
                    message=log.message,
                    details=log.details,
                )
            )
    
    return WorkflowLogsResponse(
        workflow_id=workflow_id,
        status=workflow.status,
        stages=list(stages.values()),
        bigtool_selections=bigtool_selections,
        mcp_calls=mcp_calls,
    )


# ============================================
# STREAM LOGS (SSE)
# ============================================

@router.get(
    "/{workflow_id}/stream",
    summary="Stream Workflow Logs (SSE)",
    description="""
Stream real-time logs for a workflow via Server-Sent Events (SSE).

**Connection:**
- Keeps connection open until workflow completes
- Sends events as they occur
- Automatically closes when workflow finishes

**Event format:**
```
data: {"id": 1, "event_type": "stage_start", "stage_id": "INTAKE", ...}

data: {"event": "workflow_complete", "status": "COMPLETED"}
```

**Client usage (JavaScript):**
```javascript
const eventSource = new EventSource('/api/v1/logs/wf_123/stream');
eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);
};
```
    """,
    responses={
        200: {
            "description": "SSE stream",
            "content": {"text/event-stream": {}}
        },
        404: {"description": "Workflow not found"}
    }
)
async def stream_workflow_logs(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """
    Stream real-time logs for a workflow via Server-Sent Events.
    
    Args:
        workflow_id: Workflow identifier
        db: Database session
        
    Returns:
        SSE stream of log events
    """
    # Verify workflow exists
    query = select(Workflow).where(Workflow.workflow_id == workflow_id)
    result = await db.execute(query)
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow not found: {workflow_id}",
        )
    
    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events for workflow logs."""
        last_log_id = 0
        poll_interval = 1  # seconds
        max_polls = 300  # 5 minutes max
        polls = 0
        
        while polls < max_polls:
            try:
                async with get_db_context() as session:
                    # Get new logs since last check
                    logs_query = (
                        select(AuditLog)
                        .where(
                            and_(
                                AuditLog.workflow_id == workflow_id,
                                AuditLog.id > last_log_id
                            )
                        )
                        .order_by(AuditLog.id)
                        .limit(50)
                    )
                    logs_result = await session.execute(logs_query)
                    new_logs = logs_result.scalars().all()
                    
                    # Emit new log events
                    for log in new_logs:
                        last_log_id = log.id
                        event_data = {
                            "id": log.id,
                            "event_type": log.event_type,
                            "stage_id": log.stage_id,
                            "message": log.message,
                            "details": log.details,
                            "actor_type": log.actor_type,
                            "timestamp": log.created_at.isoformat() if log.created_at else None,
                        }
                        yield f"data: {json.dumps(event_data)}\n\n"
                    
                    # Check if workflow is complete
                    wf_query = select(Workflow).where(Workflow.workflow_id == workflow_id)
                    wf_result = await session.execute(wf_query)
                    wf = wf_result.scalar_one_or_none()
                    
                    if wf and wf.status in [
                        WorkflowStatus.COMPLETED,
                        WorkflowStatus.FAILED,
                        WorkflowStatus.MANUAL_HANDOFF,
                    ]:
                        # Send completion event
                        completion_event = {
                            "event": "workflow_complete",
                            "status": wf.status,
                            "current_stage": wf.current_stage,
                            "timestamp": utc_now_iso(),
                        }
                        yield f"data: {json.dumps(completion_event)}\n\n"
                        break
                    
                    # Check if paused (HITL)
                    if wf and wf.status == WorkflowStatus.PAUSED:
                        paused_event = {
                            "event": "workflow_paused",
                            "status": wf.status,
                            "current_stage": wf.current_stage,
                            "message": "Workflow paused for human review",
                            "timestamp": utc_now_iso(),
                        }
                        yield f"data: {json.dumps(paused_event)}\n\n"
                        # Continue streaming in case workflow resumes
                
            except Exception as e:
                logger.error(f"SSE stream error: {e}")
                error_event = {
                    "event": "error",
                    "message": str(e),
                    "timestamp": utc_now_iso(),
                }
                yield f"data: {json.dumps(error_event)}\n\n"
            
            polls += 1
            await asyncio.sleep(poll_interval)
        
        # Timeout event
        timeout_event = {
            "event": "timeout",
            "message": "Stream timeout - reconnect if needed",
            "timestamp": utc_now_iso(),
        }
        yield f"data: {json.dumps(timeout_event)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        },
    )


# ============================================
# GET STAGE LOGS
# ============================================

@router.get(
    "/{workflow_id}/stages",
    response_model=dict[str, Any],
    summary="Get Logs Grouped by Stage",
    description="Get workflow logs organized by stage for easy visualization.",
)
async def get_stage_logs(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get logs grouped by workflow stage.
    
    Args:
        workflow_id: Workflow identifier
        db: Database session
        
    Returns:
        Logs organized by stage
    """
    # Get all logs
    logs_response = await get_workflow_logs(workflow_id, db)
    
    # Reformat for stage-centric view
    stages_summary = []
    for stage in logs_response.stages:
        stages_summary.append({
            "stage_id": stage.stage_id,
            "status": stage.status,
            "started_at": stage.started_at,
            "completed_at": stage.completed_at,
            "duration_ms": stage.duration_ms,
            "events_count": len(stage.entries),
            "has_errors": any(e.level == "ERROR" for e in stage.entries),
        })
    
    return {
        "workflow_id": workflow_id,
        "status": logs_response.status,
        "stages_count": len(stages_summary),
        "stages": stages_summary,
        "timestamp": utc_now_iso(),
    }


# ============================================
# GET BIGTOOL LOGS
# ============================================

@router.get(
    "/{workflow_id}/bigtool",
    response_model=dict[str, Any],
    summary="Get Bigtool Selection Logs",
    description="Get all Bigtool tool selection decisions for a workflow.",
)
async def get_bigtool_logs(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get Bigtool selection history for a workflow.
    
    Args:
        workflow_id: Workflow identifier
        db: Database session
        
    Returns:
        Bigtool selection log
    """
    # Query Bigtool selection logs
    query = (
        select(AuditLog)
        .where(
            and_(
                AuditLog.workflow_id == workflow_id,
                AuditLog.event_type == "bigtool_selection"
            )
        )
        .order_by(AuditLog.created_at)
    )
    result = await db.execute(query)
    logs = result.scalars().all()
    
    selections = []
    for log in logs:
        details = log.details or {}
        selections.append({
            "timestamp": log.created_at.isoformat() if log.created_at else None,
            "stage_id": log.stage_id,
            "capability": details.get("capability"),
            "selected_tool": details.get("selected"),
            "available_tools": details.get("available", []),
            "context": details.get("context", {}),
        })
    
    # Summarize by capability
    by_capability = {}
    for sel in selections:
        cap = sel["capability"]
        if cap not in by_capability:
            by_capability[cap] = []
        by_capability[cap].append(sel["selected_tool"])
    
    return {
        "workflow_id": workflow_id,
        "total_selections": len(selections),
        "selections": selections,
        "by_capability": by_capability,
        "timestamp": utc_now_iso(),
    }


# ============================================
# GET MCP LOGS
# ============================================

@router.get(
    "/{workflow_id}/mcp",
    response_model=dict[str, Any],
    summary="Get MCP Call Logs",
    description="Get all MCP ability calls for a workflow.",
)
async def get_mcp_logs(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get MCP call history for a workflow.
    
    Args:
        workflow_id: Workflow identifier
        db: Database session
        
    Returns:
        MCP call log
    """
    # Query MCP call logs
    query = (
        select(AuditLog)
        .where(
            and_(
                AuditLog.workflow_id == workflow_id,
                AuditLog.event_type == "mcp_call"
            )
        )
        .order_by(AuditLog.created_at)
    )
    result = await db.execute(query)
    logs = result.scalars().all()
    
    calls = []
    for log in logs:
        details = log.details or {}
        calls.append({
            "timestamp": log.created_at.isoformat() if log.created_at else None,
            "stage_id": log.stage_id,
            "server": details.get("server"),
            "ability": details.get("ability"),
            "duration_ms": details.get("duration_ms"),
        })
    
    # Summarize by server
    by_server = {"COMMON": 0, "ATLAS": 0}
    for call in calls:
        server = call["server"]
        if server in by_server:
            by_server[server] += 1
    
    return {
        "workflow_id": workflow_id,
        "total_calls": len(calls),
        "calls": calls,
        "by_server": by_server,
        "timestamp": utc_now_iso(),
    }
