"""
Bigtool - Dynamic tool selection for invoice processing.

Provides:
- BigtoolPicker: Rule-based + LLM fallback tool selection
- ToolRegistry: Tool registration and discovery
- BaseTool: Abstract base class for tool implementations

Capabilities:
- ocr: google_vision, tesseract, aws_textract
- enrichment: clearbit, people_data_labs, vendor_db
- erp_connector: sap_sandbox, netsuite, mock_erp
- db: postgres, sqlite, dynamodb
- email: sendgrid, ses, smtp
- storage: s3, gcs, local_fs

Usage:
    from app.bigtool import get_bigtool_picker
    
    picker = get_bigtool_picker()
    tool_name = picker.select("ocr", {"document_type": "invoice"})
"""

from app.bigtool.base import (
    BaseTool,
    BaseOCRTool,
    BaseEnrichmentTool,
    BaseERPConnector,
    BaseStorageTool,
    BaseEmailTool,
    BaseDBTool,
    ToolMetadata,
    ToolResult,
    ToolProtocol,
)
from app.bigtool.registry import ToolRegistry, get_tool_registry
from app.bigtool.picker import BigtoolPicker, get_bigtool_picker


__all__ = [
    # Base classes
    "BaseTool",
    "BaseOCRTool",
    "BaseEnrichmentTool",
    "BaseERPConnector",
    "BaseStorageTool",
    "BaseEmailTool",
    "BaseDBTool",
    "ToolMetadata",
    "ToolResult",
    "ToolProtocol",
    # Registry
    "ToolRegistry",
    "get_tool_registry",
    # Picker
    "BigtoolPicker",
    "get_bigtool_picker",
]

