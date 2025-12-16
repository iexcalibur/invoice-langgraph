"""CHECKPOINT_HITL node - Create checkpoint for human review."""

from typing import Any

from app.graph.state import InvoiceState
from app.config import StageID, WorkflowStatus, get_settings
from app.utils.logger import get_workflow_logger
from app.utils.helpers import generate_checkpoint_id, generate_review_url
from app.mcp import get_mcp_router
from app.bigtool import get_bigtool_picker


async def checkpoint_node(state: InvoiceState) -> dict[str, Any]:
    """
    CHECKPOINT_HITL Stage - Create checkpoint for human review.
    
    - Persist full workflow state
    - Create review ticket
    - Generate review URL
    - Pause workflow
    """
    workflow_id = state.get("workflow_id", "unknown")
    logger = get_workflow_logger(workflow_id)
    mcp = get_mcp_router()
    bigtool = get_bigtool_picker()
    settings = get_settings()
    
    logger.stage_start(StageID.CHECKPOINT_HITL)
    
    # Generate checkpoint ID
    checkpoint_id = generate_checkpoint_id(workflow_id)
    
    # Select DB tool
    db_tool = bigtool.select("db", {"operation": "write"})
    logger.bigtool_selection("db", db_tool, ["postgres", "sqlite", "dynamodb"])
    
    # Build paused reason
    match_score = state.get("match_score", 0)
    match_evidence = state.get("match_evidence", {})
    paused_reason = f"Two-way match failed. Score: {match_score:.2f} (threshold: {settings.match_threshold})"
    
    # Save checkpoint via MCP COMMON
    checkpoint_result = mcp.call("save_checkpoint", {
        "checkpoint_id": checkpoint_id,
        "workflow_id": workflow_id,
        "state_blob": dict(state),
        "paused_reason": paused_reason,
        "db_tool": db_tool,
    })
    logger.mcp_call("COMMON", "save_checkpoint")
    
    # Generate review URL
    review_url = generate_review_url(checkpoint_id, settings.frontend_url)
    
    logger.checkpoint_created(checkpoint_id, paused_reason)
    logger.stage_complete(StageID.CHECKPOINT_HITL)
    
    return {
        "checkpoint_id": checkpoint_id,
        "review_url": review_url,
        "paused_reason": paused_reason,
        "status": WorkflowStatus.PAUSED,
        "current_stage": StageID.CHECKPOINT_HITL,
    }
