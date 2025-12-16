"""APPROVE node - Apply approval policy."""

from typing import Any

from app.graph.state import InvoiceState
from app.config import StageID
from app.utils.logger import get_workflow_logger
from app.mcp import get_mcp_router


async def approve_node(state: InvoiceState) -> dict[str, Any]:
    """
    APPROVE Stage - Apply approval policy.
    
    - Auto-approve under threshold
    - Escalate above threshold
    """
    workflow_id = state.get("workflow_id", "unknown")
    logger = get_workflow_logger(workflow_id)
    mcp = get_mcp_router()
    
    logger.stage_start(StageID.APPROVE)
    
    raw_payload = state.get("raw_payload", {})
    invoice_amount = raw_payload.get("amount", 0)
    
    # Apply approval policy via MCP COMMON
    approval_result = mcp.call("apply_approval_policy", {
        "invoice_id": state.get("invoice_id"),
        "amount": invoice_amount,
        "vendor": state.get("vendor_profile", {}).get("normalized_name", ""),
        "risk_score": state.get("risk_score", 0),
    })
    logger.mcp_call("COMMON", "apply_approval_policy")
    
    # Simple approval logic
    AUTO_APPROVE_THRESHOLD = 10000
    
    if invoice_amount <= AUTO_APPROVE_THRESHOLD:
        approval_status = "AUTO_APPROVED"
        approver_id = "SYSTEM"
    else:
        approval_status = "ESCALATED"
        approver_id = "finance_manager"
    
    logger.info(f"Approval status: {approval_status}")
    logger.stage_complete(StageID.APPROVE)
    
    return {
        "approval_status": approval_status,
        "approver_id": approver_id,
        "current_stage": StageID.APPROVE,
    }
