"""PREPARE node - Normalize and enrich vendor data."""

from typing import Any

from app.graph.state import InvoiceState
from app.config import StageID
from app.utils.logger import get_workflow_logger
from app.mcp import get_mcp_router
from app.bigtool import get_bigtool_picker


async def prepare_node(state: InvoiceState) -> dict[str, Any]:
    """
    PREPARE Stage - Normalize and enrich.
    
    - Normalize vendor name
    - Enrich vendor data (PAN/GST/TaxID)
    - Compute validation flags
    """
    workflow_id = state.get("workflow_id", "unknown")
    logger = get_workflow_logger(workflow_id)
    mcp = get_mcp_router()
    bigtool = get_bigtool_picker()
    
    logger.stage_start(StageID.PREPARE)
    
    raw_payload = state.get("raw_payload", {})
    vendor_name = raw_payload.get("vendor_name", "")
    vendor_tax_id = raw_payload.get("vendor_tax_id", "")
    
    # Normalize vendor via MCP COMMON
    normalize_result = mcp.call("normalize_vendor", {"vendor_name": vendor_name})
    logger.mcp_call("COMMON", "normalize_vendor")
    
    # Select enrichment provider
    enrichment_tool = bigtool.select("enrichment", {"vendor_name": vendor_name})
    logger.bigtool_selection("enrichment", enrichment_tool, ["clearbit", "people_data_labs", "vendor_db"])
    
    # Enrich vendor via MCP ATLAS
    enrich_result = mcp.call("enrich_vendor", {
        "vendor_name": normalize_result.get("normalized_name", vendor_name),
        "tax_id": vendor_tax_id,
        "provider": enrichment_tool,
    })
    logger.mcp_call("ATLAS", "enrich_vendor")
    
    # Compute flags via MCP COMMON
    flags_result = mcp.call("compute_flags", {
        "vendor_profile": enrich_result,
        "invoice": raw_payload,
    })
    logger.mcp_call("COMMON", "compute_flags")
    
    vendor_profile = {
        "normalized_name": normalize_result.get("normalized_name", vendor_name),
        "tax_id": vendor_tax_id,
        "enrichment_meta": enrich_result,
    }
    
    normalized_invoice = {
        "amount": raw_payload.get("amount", 0),
        "currency": raw_payload.get("currency", "USD"),
        "line_items": raw_payload.get("line_items", []),
    }
    
    flags = {
        "missing_info": flags_result.get("missing_info", []),
        "risk_score": flags_result.get("risk_score", 0.0),
    }
    
    logger.stage_complete(StageID.PREPARE)
    
    return {
        "vendor_profile": vendor_profile,
        "normalized_invoice": normalized_invoice,
        "flags": flags,
        "enrichment_provider_used": enrichment_tool,
        "normalized_name": vendor_profile["normalized_name"],
        "risk_score": flags["risk_score"],
        "missing_info": flags["missing_info"],
        "current_stage": StageID.PREPARE,
    }
