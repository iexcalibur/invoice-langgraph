"""MATCH_TWO_WAY node - Compute match score between invoice and PO."""

from typing import Any

from app.graph.state import InvoiceState
from app.config import StageID, MatchResult, get_settings
from app.utils.logger import get_workflow_logger
from app.utils.helpers import calculate_match_score
from app.mcp import get_mcp_router


async def match_node(state: InvoiceState) -> dict[str, Any]:
    """
    MATCH_TWO_WAY Stage - Two-way matching.
    
    - Compare invoice vs PO
    - Compute match score
    - Determine if human review needed
    """
    workflow_id = state.get("workflow_id", "unknown")
    logger = get_workflow_logger(workflow_id)
    mcp = get_mcp_router()
    settings = get_settings()
    
    logger.stage_start(StageID.MATCH_TWO_WAY)
    
    raw_payload = state.get("raw_payload", {})
    matched_pos = state.get("matched_pos", [])
    
    invoice_amount = raw_payload.get("amount", 0)
    threshold = settings.match_threshold
    tolerance_pct = settings.two_way_tolerance_pct
    
    # Compute match score via MCP COMMON
    match_result = mcp.call("compute_match_score", {
        "invoice_amount": invoice_amount,
        "purchase_orders": matched_pos,
        "threshold": threshold,
        "tolerance_pct": tolerance_pct,
    })
    logger.mcp_call("COMMON", "compute_match_score")
    
    # Use computed or calculate score
    if matched_pos:
        po_amount = sum(po.get("amount", 0) for po in matched_pos)
        score = calculate_match_score(invoice_amount, po_amount, tolerance_pct)
    else:
        score = 0.0
    
    match_status = MatchResult.MATCHED if score >= threshold else MatchResult.FAILED
    
    match_evidence = {
        "invoice_amount": invoice_amount,
        "po_total": sum(po.get("amount", 0) for po in matched_pos),
        "pos_count": len(matched_pos),
        "threshold_used": threshold,
        "difference_pct": abs(invoice_amount - sum(po.get("amount", 0) for po in matched_pos)) / max(invoice_amount, 1) * 100,
    }
    
    logger.info(f"Match score: {score:.2f}, result: {match_status}")
    logger.stage_complete(StageID.MATCH_TWO_WAY)
    
    return {
        "match_score": score,
        "match_result": match_status,
        "tolerance_pct": tolerance_pct,
        "match_evidence": match_evidence,
        "current_stage": StageID.MATCH_TWO_WAY,
    }
