"""RECONCILE node - Build accounting entries."""

from typing import Any
from datetime import datetime

from app.graph.state import InvoiceState
from app.config import StageID
from app.utils.logger import get_workflow_logger
from app.mcp import get_mcp_router


async def reconcile_node(state: InvoiceState) -> dict[str, Any]:
    """
    RECONCILE Stage - Build accounting entries.
    
    - Create debit/credit entries
    - Build reconciliation report
    """
    workflow_id = state.get("workflow_id", "unknown")
    logger = get_workflow_logger(workflow_id)
    mcp = get_mcp_router()
    
    logger.stage_start(StageID.RECONCILE)
    
    raw_payload = state.get("raw_payload", {})
    vendor_profile = state.get("vendor_profile", {})
    matched_pos = state.get("matched_pos", [])
    
    invoice_amount = raw_payload.get("amount", 0)
    currency = raw_payload.get("currency", "USD")
    
    # Build accounting entries via MCP COMMON
    accounting_result = mcp.call("build_accounting_entries", {
        "invoice_id": state.get("invoice_id"),
        "vendor": vendor_profile.get("normalized_name", ""),
        "amount": invoice_amount,
        "currency": currency,
        "purchase_orders": matched_pos,
    })
    logger.mcp_call("COMMON", "build_accounting_entries")
    
    # Build entries
    accounting_entries = [
        {
            "entry_id": f"JE-{state.get('invoice_id')}-001",
            "type": "DEBIT",
            "account": "2100-Accounts Payable",
            "amount": invoice_amount,
            "currency": currency,
            "description": f"Invoice from {vendor_profile.get('normalized_name', 'Unknown')}",
        },
        {
            "entry_id": f"JE-{state.get('invoice_id')}-002",
            "type": "CREDIT",
            "account": "5000-Expenses",
            "amount": invoice_amount,
            "currency": currency,
            "description": f"Expense for invoice {state.get('invoice_id')}",
        },
    ]
    
    reconciliation_report = {
        "invoice_id": state.get("invoice_id"),
        "vendor": vendor_profile.get("normalized_name", ""),
        "total_amount": invoice_amount,
        "currency": currency,
        "entries_count": len(accounting_entries),
        "reconciled_at": datetime.utcnow().isoformat(),
        "matched_pos_count": len(matched_pos),
    }
    
    logger.stage_complete(StageID.RECONCILE)
    
    return {
        "accounting_entries": accounting_entries,
        "reconciliation_report": reconciliation_report,
        "current_stage": StageID.RECONCILE,
    }
