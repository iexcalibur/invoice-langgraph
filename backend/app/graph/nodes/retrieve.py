"""RETRIEVE node - Fetch PO, GRN, and history from ERP."""

from typing import Any

from app.graph.state import InvoiceState
from app.config import StageID
from app.utils.logger import get_workflow_logger
from app.mcp import get_mcp_router
from app.bigtool import get_bigtool_picker


async def retrieve_node(state: InvoiceState) -> dict[str, Any]:
    """
    RETRIEVE Stage - Fetch ERP data.
    
    - Fetch Purchase Orders
    - Fetch Goods Received Notes
    - Fetch historical invoices
    """
    workflow_id = state.get("workflow_id", "unknown")
    logger = get_workflow_logger(workflow_id)
    mcp = get_mcp_router()
    bigtool = get_bigtool_picker()
    
    logger.stage_start(StageID.RETRIEVE)
    
    raw_payload = state.get("raw_payload", {})
    vendor_profile = state.get("vendor_profile", {})
    detected_pos = state.get("detected_pos", [])
    
    # Select ERP connector
    erp_tool = bigtool.select("erp_connector", {"vendor": vendor_profile.get("normalized_name", "")})
    logger.bigtool_selection("erp_connector", erp_tool, ["sap_sandbox", "netsuite", "mock_erp"])
    
    # Fetch POs via MCP ATLAS
    po_result = mcp.call("fetch_po", {
        "vendor_name": vendor_profile.get("normalized_name", ""),
        "po_numbers": detected_pos,
        "connector": erp_tool,
    })
    logger.mcp_call("ATLAS", "fetch_po")
    
    # Fetch GRNs via MCP ATLAS
    grn_result = mcp.call("fetch_grn", {
        "po_ids": [po.get("po_id") for po in po_result.get("purchase_orders", [])],
        "connector": erp_tool,
    })
    logger.mcp_call("ATLAS", "fetch_grn")
    
    # Fetch history via MCP ATLAS
    history_result = mcp.call("fetch_history", {
        "vendor_name": vendor_profile.get("normalized_name", ""),
        "connector": erp_tool,
    })
    logger.mcp_call("ATLAS", "fetch_history")
    
    logger.stage_complete(StageID.RETRIEVE)
    
    return {
        "matched_pos": po_result.get("purchase_orders", []),
        "matched_grns": grn_result.get("grns", []),
        "history": history_result.get("invoices", []),
        "erp_connector_used": erp_tool,
        "current_stage": StageID.RETRIEVE,
    }
