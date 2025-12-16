"""NOTIFY node - Send notifications."""

from typing import Any

from app.graph.state import InvoiceState
from app.config import StageID
from app.utils.logger import get_workflow_logger
from app.mcp import get_mcp_router
from app.bigtool import get_bigtool_picker


async def notify_node(state: InvoiceState) -> dict[str, Any]:
    """
    NOTIFY Stage - Send notifications.
    
    - Notify vendor
    - Notify internal finance team
    """
    workflow_id = state.get("workflow_id", "unknown")
    logger = get_workflow_logger(workflow_id)
    mcp = get_mcp_router()
    bigtool = get_bigtool_picker()
    
    logger.stage_start(StageID.NOTIFY)
    
    raw_payload = state.get("raw_payload", {})
    vendor_profile = state.get("vendor_profile", {})
    
    # Select email provider
    email_tool = bigtool.select("email", {"volume": "low"})
    logger.bigtool_selection("email", email_tool, ["sendgrid", "smartlead", "ses"])
    
    # Notify vendor via MCP ATLAS
    vendor_notify = mcp.call("notify_vendor", {
        "vendor_name": vendor_profile.get("normalized_name", ""),
        "invoice_id": state.get("invoice_id"),
        "amount": raw_payload.get("amount", 0),
        "scheduled_payment_id": state.get("scheduled_payment_id"),
        "provider": email_tool,
    })
    logger.mcp_call("ATLAS", "notify_vendor")
    
    # Notify finance team via MCP ATLAS
    finance_notify = mcp.call("notify_finance_team", {
        "invoice_id": state.get("invoice_id"),
        "vendor": vendor_profile.get("normalized_name", ""),
        "amount": raw_payload.get("amount", 0),
        "approval_status": state.get("approval_status"),
        "provider": email_tool,
    })
    logger.mcp_call("ATLAS", "notify_finance_team")
    
    notify_status = {
        "vendor": {"sent": True, "provider": email_tool},
        "finance_team": {"sent": True, "provider": email_tool},
    }
    
    notified_parties = ["vendor", "finance_team"]
    
    logger.stage_complete(StageID.NOTIFY)
    
    return {
        "notify_status": notify_status,
        "notified_parties": notified_parties,
        "email_provider_used": email_tool,
        "current_stage": StageID.NOTIFY,
    }
