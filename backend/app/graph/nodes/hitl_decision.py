"""HITL_DECISION node - Process human review decision."""

from typing import Any

from app.graph.state import InvoiceState
from app.config import StageID, WorkflowStatus, HumanDecisionType
from app.utils.logger import get_workflow_logger
from app.mcp import get_mcp_router


async def hitl_decision_node(state: InvoiceState) -> dict[str, Any]:
    """
    HITL_DECISION Stage - Process human decision.
    
    - Read human decision (ACCEPT/REJECT)
    - Route to next stage accordingly
    """
    workflow_id = state.get("workflow_id", "unknown")
    logger = get_workflow_logger(workflow_id)
    mcp = get_mcp_router()
    
    logger.stage_start(StageID.HITL_DECISION)
    
    # Get human decision from state (set by review service)
    human_decision = state.get("human_decision")
    reviewer_id = state.get("reviewer_id")
    reviewer_notes = state.get("reviewer_notes", "")
    checkpoint_id = state.get("checkpoint_id")
    
    # Log the decision
    logger.workflow_resumed(checkpoint_id or "unknown", human_decision or "unknown")
    
    # Process via MCP ATLAS
    decision_result = mcp.call("human_review_action", {
        "checkpoint_id": checkpoint_id,
        "decision": human_decision,
        "reviewer_id": reviewer_id,
        "notes": reviewer_notes,
    })
    logger.mcp_call("ATLAS", "human_review_action")
    
    # Determine next stage and status
    if human_decision == HumanDecisionType.ACCEPT:
        next_stage = StageID.RECONCILE
        status = WorkflowStatus.RUNNING
    else:
        next_stage = StageID.COMPLETE
        status = WorkflowStatus.MANUAL_HANDOFF
    
    logger.stage_complete(StageID.HITL_DECISION)
    
    return {
        "human_decision": human_decision,
        "reviewer_id": reviewer_id,
        "reviewer_notes": reviewer_notes,
        "resume_token": workflow_id,
        "next_stage": next_stage,
        "status": status,
        "current_stage": StageID.HITL_DECISION,
    }
