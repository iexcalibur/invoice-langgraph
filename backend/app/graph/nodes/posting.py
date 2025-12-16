"""POSTING node - Post to ERP and schedule payment."""

from typing import Any

from app.graph.state import InvoiceState
from app.config import StageID
from app.utils.logger import get_workflow_logger
from app.utils.helpers import generate_id
from app.mcp import get_mcp_router
from app.bigtool import get_bigtool_picker


async def posting_node(state: InvoiceState) -> dict[str, Any]:
    """
    POSTING Stage - Post to ERP and schedule payment.
    
    - Post journal entries to ERP
    - Schedule payment
    """
    workflow_id = state.get("workflow_id", "unknown")
    logger = get_workflow_logger(workflow_id)
    mcp = get_mcp_router()
    bigtool = get_bigtool_picker()
    
    logger.stage_start(StageID.POSTING)
    
    accounting_entries = state.get("accounting_entries", [])
    raw_payload = state.get("raw_payload", {})
    
    # Select ERP connector
    erp_tool = bigtool.select("erp_connector", {"operation": "write"})
    logger.bigtool_selection("erp_connector", erp_tool, ["sap_sandbox", "netsuite", "mock_erp"])
    
    # Post to ERP via MCP ATLAS
    post_result = mcp.call("post_to_erp", {
        "invoice_id": state.get("invoice_id"),
        "entries": accounting_entries,
        "connector": erp_tool,
    })
    logger.mcp_call("ATLAS", "post_to_erp")
    
    # Schedule payment via MCP ATLAS
    payment_result = mcp.call("schedule_payment", {
        "invoice_id": state.get("invoice_id"),
        "amount": raw_payload.get("amount", 0),
        "due_date": raw_payload.get("due_date"),
        "vendor": state.get("vendor_profile", {}).get("normalized_name", ""),
    })
    logger.mcp_call("ATLAS", "schedule_payment")
    
    erp_txn_id = generate_id("ERP-TXN")
    scheduled_payment_id = generate_id("PAY")
    
    logger.stage_complete(StageID.POSTING)
    
    return {
        "posted": True,
        "erp_txn_id": erp_txn_id,
        "scheduled_payment_id": scheduled_payment_id,
        "current_stage": StageID.POSTING,
    }
