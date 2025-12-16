"""INTAKE node - Accept and validate invoice payload."""

from typing import Any
from datetime import datetime

from app.graph.state import InvoiceState
from app.config import StageID
from app.utils.logger import get_workflow_logger
from app.utils.helpers import generate_id
from app.mcp import get_mcp_router
from app.bigtool import get_bigtool_picker


async def intake_node(state: InvoiceState) -> dict[str, Any]:
    """
    INTAKE Stage - Accept invoice payload.
    
    - Validate schema
    - Persist raw invoice
    - Return raw_id and ingest timestamp
    """
    workflow_id = state.get("workflow_id", "unknown")
    logger = get_workflow_logger(workflow_id)
    mcp = get_mcp_router()
    bigtool = get_bigtool_picker()
    
    logger.stage_start(StageID.INTAKE)
    
    # Select storage provider
    storage_tool = bigtool.select("storage", {"size": "small"})
    logger.bigtool_selection("storage", storage_tool, ["s3", "gcs", "local_fs"])
    
    # Get raw payload
    raw_payload = state.get("raw_payload", {})
    
    # Validate schema via MCP COMMON
    validation_result = mcp.call("validate_schema", {"payload": raw_payload})
    logger.mcp_call("COMMON", "validate_schema")
    
    # Persist raw invoice
    raw_id = generate_id("raw")
    persist_result = mcp.call("persist_raw_invoice", {
        "raw_id": raw_id,
        "payload": raw_payload,
        "storage": storage_tool,
    })
    logger.mcp_call("COMMON", "persist_raw_invoice")
    
    ingest_ts = datetime.utcnow().isoformat()
    
    logger.stage_complete(StageID.INTAKE)
    
    return {
        "raw_id": raw_id,
        "ingest_ts": ingest_ts,
        "validated": validation_result.get("valid", True),
        "storage_provider_used": storage_tool,
        "current_stage": StageID.INTAKE,
    }
