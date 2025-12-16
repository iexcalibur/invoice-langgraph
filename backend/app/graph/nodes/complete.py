"""COMPLETE node - Finalize workflow."""

from typing import Any
from datetime import datetime

from app.graph.state import InvoiceState
from app.config import StageID, WorkflowStatus
from app.utils.logger import get_workflow_logger
from app.mcp import get_mcp_router
from app.bigtool import get_bigtool_picker


async def complete_node(state: InvoiceState) -> dict[str, Any]:
    """
    COMPLETE Stage - Finalize workflow.
    
    - Produce final payload
    - Create audit log
    - Mark workflow complete
    """
    workflow_id = state.get("workflow_id", "unknown")
    logger = get_workflow_logger(workflow_id)
    mcp = get_mcp_router()
    bigtool = get_bigtool_picker()
    
    logger.stage_start(StageID.COMPLETE)
    
    # Determine final status
    current_status = state.get("status", WorkflowStatus.RUNNING)
    if current_status == WorkflowStatus.MANUAL_HANDOFF:
        final_status = WorkflowStatus.MANUAL_HANDOFF
    else:
        final_status = WorkflowStatus.COMPLETED
    
    # Select DB tool
    db_tool = bigtool.select("db", {"operation": "write"})
    logger.bigtool_selection("db", db_tool, ["postgres", "sqlite", "dynamodb"])
    
    # Build final payload
    final_payload = {
        "workflow_id": workflow_id,
        "invoice_id": state.get("invoice_id"),
        "status": final_status,
        "vendor": state.get("vendor_profile", {}).get("normalized_name", ""),
        "amount": state.get("raw_payload", {}).get("amount", 0),
        "currency": state.get("raw_payload", {}).get("currency", "USD"),
        "match_score": state.get("match_score"),
        "match_result": state.get("match_result"),
        "human_decision": state.get("human_decision"),
        "approval_status": state.get("approval_status"),
        "erp_txn_id": state.get("erp_txn_id"),
        "scheduled_payment_id": state.get("scheduled_payment_id"),
        "completed_at": datetime.utcnow().isoformat(),
    }
    
    # Build audit log
    audit_log = [
        {"stage": "INTAKE", "status": "completed", "timestamp": state.get("ingest_ts")},
        {"stage": "UNDERSTAND", "status": "completed", "ocr_provider": state.get("ocr_provider_used")},
        {"stage": "PREPARE", "status": "completed", "enrichment_provider": state.get("enrichment_provider_used")},
        {"stage": "RETRIEVE", "status": "completed", "erp_connector": state.get("erp_connector_used")},
        {"stage": "MATCH_TWO_WAY", "status": "completed", "score": state.get("match_score")},
    ]
    
    if state.get("checkpoint_id"):
        audit_log.append({"stage": "CHECKPOINT_HITL", "status": "completed", "checkpoint_id": state.get("checkpoint_id")})
        audit_log.append({"stage": "HITL_DECISION", "status": "completed", "decision": state.get("human_decision")})
    
    if final_status != WorkflowStatus.MANUAL_HANDOFF:
        audit_log.extend([
            {"stage": "RECONCILE", "status": "completed"},
            {"stage": "APPROVE", "status": "completed", "approval": state.get("approval_status")},
            {"stage": "POSTING", "status": "completed", "erp_txn": state.get("erp_txn_id")},
            {"stage": "NOTIFY", "status": "completed", "parties": state.get("notified_parties")},
        ])
    
    audit_log.append({"stage": "COMPLETE", "status": "completed", "final_status": final_status})
    
    # Output final payload via MCP COMMON
    output_result = mcp.call("output_final_payload", {
        "payload": final_payload,
        "audit_log": audit_log,
        "db_tool": db_tool,
    })
    logger.mcp_call("COMMON", "output_final_payload")
    
    logger.workflow_complete(final_status)
    logger.stage_complete(StageID.COMPLETE)
    
    return {
        "final_payload": final_payload,
        "audit_log": audit_log,
        "status": final_status,
        "current_stage": StageID.COMPLETE,
    }
