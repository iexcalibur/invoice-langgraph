"""UNDERSTAND node - OCR and parse invoice."""

from typing import Any

from app.graph.state import InvoiceState
from app.config import StageID
from app.utils.logger import get_workflow_logger
from app.mcp import get_mcp_router
from app.bigtool import get_bigtool_picker


async def understand_node(state: InvoiceState) -> dict[str, Any]:
    """
    UNDERSTAND Stage - OCR and parse invoice.
    
    - Run OCR on attachments
    - Parse line items
    - Extract dates and amounts
    """
    workflow_id = state.get("workflow_id", "unknown")
    logger = get_workflow_logger(workflow_id)
    mcp = get_mcp_router()
    bigtool = get_bigtool_picker()
    
    logger.stage_start(StageID.UNDERSTAND)
    
    raw_payload = state.get("raw_payload", {})
    attachments = raw_payload.get("attachments", [])
    
    # Select OCR provider
    ocr_tool = bigtool.select("ocr", {"document_type": "invoice"})
    logger.bigtool_selection("ocr", ocr_tool, ["google_vision", "tesseract", "aws_textract"])
    
    # Run OCR via MCP ATLAS
    ocr_result = mcp.call("ocr_extract", {
        "attachments": attachments,
        "provider": ocr_tool,
    })
    logger.mcp_call("ATLAS", "ocr_extract")
    
    # Parse line items via MCP COMMON
    parse_result = mcp.call("parse_line_items", {
        "text": ocr_result.get("extracted_text", ""),
        "raw_payload": raw_payload,
    })
    logger.mcp_call("COMMON", "parse_line_items")
    
    # Build parsed invoice structure
    parsed_invoice = {
        "invoice_text": ocr_result.get("extracted_text", ""),
        "parsed_line_items": parse_result.get("line_items", raw_payload.get("line_items", [])),
        "detected_pos": parse_result.get("detected_pos", []),
        "currency": raw_payload.get("currency", "USD"),
        "parsed_dates": {
            "invoice_date": raw_payload.get("invoice_date"),
            "due_date": raw_payload.get("due_date"),
        },
        "amount": raw_payload.get("amount", 0),
    }
    
    logger.stage_complete(StageID.UNDERSTAND)
    
    return {
        "parsed_invoice": parsed_invoice,
        "ocr_provider_used": ocr_tool,
        "invoice_text": parsed_invoice["invoice_text"],
        "parsed_line_items": parsed_invoice["parsed_line_items"],
        "detected_pos": parsed_invoice["detected_pos"],
        "parsed_dates": parsed_invoice["parsed_dates"],
        "current_stage": StageID.UNDERSTAND,
    }
