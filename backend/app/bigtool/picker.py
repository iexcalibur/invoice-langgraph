"""
BigtoolPicker - Rule-based + LLM fallback tool selection.

Selects the appropriate tool from a pool based on:
1. Rule-based matching (primary) - fast, deterministic
2. LLM fallback (optional) - for complex/ambiguous cases

Capabilities:
- ocr: google_vision, tesseract, aws_textract
- enrichment: clearbit, people_data_labs, vendor_db
- erp_connector: sap_sandbox, netsuite, mock_erp
- db: postgres, sqlite, dynamodb
- email: sendgrid, ses, smtp
- storage: s3, gcs, local_fs
"""

from typing import Any
from datetime import datetime

from app.bigtool.registry import get_tool_registry, ToolRegistry
from app.config import get_settings, BigtoolCapability, DEFAULT_TOOL_SELECTIONS
from app.utils.logger import logger


class BigtoolPicker:
    """
    Bigtool selection engine with rule-based + LLM fallback.
    
    Usage:
        picker = BigtoolPicker()
        tool_name = picker.select("ocr", {"document_type": "invoice", "quality": "high"})
    """
    
    def __init__(self, registry: ToolRegistry | None = None):
        self.registry = registry or get_tool_registry()
        self.settings = get_settings()
        self._selection_log: list[dict[str, Any]] = []
    
    def select(self, capability: str, context: dict[str, Any] | None = None) -> str:
        """
        Select the best tool for a capability based on context.
        
        Args:
            capability: Tool capability (ocr, enrichment, erp_connector, db, email, storage)
            context: Optional context for selection (document_type, size, vendor, etc.)
            
        Returns:
            Selected tool name
        """
        context = context or {}
        
        # Get available tools for capability
        available_tools = self.registry.list_tools(capability)
        
        if not available_tools:
            logger.warning(f"No tools available for capability: {capability}")
            return self._get_default(capability)
        
        # Try rule-based selection first
        selected = self._rule_based_select(capability, context, available_tools)
        
        # If rule-based fails and LLM is available, use LLM fallback
        if not selected and self.settings.anthropic_api_key:
            selected = self._llm_select(capability, context, available_tools)
        
        # Fall back to default if nothing else works
        if not selected:
            selected = self._get_default(capability)
        
        # Log the selection
        self._log_selection(capability, selected, context, available_tools)
        
        return selected
    
    def _rule_based_select(
        self,
        capability: str,
        context: dict[str, Any],
        available_tools: list[str],
    ) -> str | None:
        """
        Rule-based tool selection.
        
        Applies capability-specific rules based on context.
        """
        
        # === OCR SELECTION ===
        if capability == BigtoolCapability.OCR:
            return self._select_ocr(context, available_tools)
        
        # === ENRICHMENT SELECTION ===
        if capability == BigtoolCapability.ENRICHMENT:
            return self._select_enrichment(context, available_tools)
        
        # === ERP CONNECTOR SELECTION ===
        if capability == BigtoolCapability.ERP_CONNECTOR:
            return self._select_erp(context, available_tools)
        
        # === DATABASE SELECTION ===
        if capability == BigtoolCapability.DB:
            return self._select_db(context, available_tools)
        
        # === EMAIL SELECTION ===
        if capability == BigtoolCapability.EMAIL:
            return self._select_email(context, available_tools)
        
        # === STORAGE SELECTION ===
        if capability == BigtoolCapability.STORAGE:
            return self._select_storage(context, available_tools)
        
        # No specific rules, return first available
        return available_tools[0] if available_tools else None
    
    def _select_ocr(self, context: dict[str, Any], available: list[str]) -> str:
        """Select OCR tool based on document characteristics."""
        document_type = context.get("document_type", "").lower()
        quality = context.get("quality", "standard")
        language = context.get("language", "en")
        has_tables = context.get("has_tables", False)
        
        # High-quality invoices with tables → Google Vision (best accuracy)
        if quality == "high" or has_tables:
            if "google_vision" in available:
                return "google_vision"
        
        # AWS for multi-page documents
        if context.get("page_count", 1) > 5:
            if "aws_textract" in available:
                return "aws_textract"
        
        # Simple documents or cost-sensitive → Tesseract
        if quality == "low" or context.get("cost_sensitive", False):
            if "tesseract" in available:
                return "tesseract"
        
        # Default to Google Vision for invoices
        if document_type == "invoice" and "google_vision" in available:
            return "google_vision"
        
        # Fall back to first available
        return available[0] if available else None
    
    def _select_enrichment(self, context: dict[str, Any], available: list[str]) -> str:
        """Select enrichment tool based on vendor/data needs."""
        vendor_type = context.get("vendor_type", "").lower()
        enrichment_type = context.get("enrichment_type", "").lower()
        region = context.get("region", "us")
        
        # Internal vendor database for known vendors
        if context.get("is_known_vendor", False):
            if "vendor_db" in available:
                return "vendor_db"
        
        # B2B company data → Clearbit
        if vendor_type in ["business", "b2b", "enterprise"]:
            if "clearbit" in available:
                return "clearbit"
        
        # Contact/person enrichment → People Data Labs
        if enrichment_type in ["contact", "person", "employee"]:
            if "people_data_labs" in available:
                return "people_data_labs"
        
        # Default to Clearbit for company enrichment
        if "clearbit" in available:
            return "clearbit"
        
        return available[0] if available else None
    
    def _select_erp(self, context: dict[str, Any], available: list[str]) -> str:
        """Select ERP connector based on target system."""
        erp_system = context.get("erp_system", "").lower()
        operation = context.get("operation", "read")
        
        # Explicit ERP system specified
        if "sap" in erp_system and "sap_sandbox" in available:
            return "sap_sandbox"
        if "netsuite" in erp_system and "netsuite" in available:
            return "netsuite"
        
        # For demo/testing, use mock ERP
        if self.settings.is_development or context.get("use_mock", False):
            if "mock_erp" in available:
                return "mock_erp"
        
        # Default to mock for safety
        return "mock_erp" if "mock_erp" in available else available[0] if available else None
    
    def _select_db(self, context: dict[str, Any], available: list[str]) -> str:
        """Select database tool based on operation requirements."""
        operation = context.get("operation", "read")
        data_size = context.get("data_size", "small")
        
        # Large data or production → Postgres
        if data_size == "large" or self.settings.is_production:
            if "postgres" in available:
                return "postgres"
        
        # Serverless/AWS environment → DynamoDB
        if context.get("serverless", False):
            if "dynamodb" in available:
                return "dynamodb"
        
        # Development/demo → SQLite
        if self.settings.is_development:
            if "sqlite" in available:
                return "sqlite"
        
        # Default to SQLite for simplicity
        return "sqlite" if "sqlite" in available else available[0] if available else None
    
    def _select_email(self, context: dict[str, Any], available: list[str]) -> str:
        """Select email tool based on volume and requirements."""
        volume = context.get("volume", "low")
        email_type = context.get("email_type", "transactional")
        
        # High volume transactional → SendGrid
        if volume == "high" or email_type == "transactional":
            if "sendgrid" in available:
                return "sendgrid"
        
        # AWS environment → SES
        if context.get("aws_environment", False):
            if "ses" in available:
                return "ses"
        
        # Simple SMTP for internal/testing
        if self.settings.is_development:
            if "smtp" in available:
                return "smtp"
        
        # Default to SendGrid
        return "sendgrid" if "sendgrid" in available else available[0] if available else None
    
    def _select_storage(self, context: dict[str, Any], available: list[str]) -> str:
        """Select storage tool based on file characteristics."""
        file_size = context.get("size", "small")
        storage_class = context.get("storage_class", "standard")
        
        # Large files or production → S3
        if file_size == "large" or self.settings.is_production:
            if "s3" in available:
                return "s3"
        
        # GCP environment → GCS
        if context.get("gcp_environment", False):
            if "gcs" in available:
                return "gcs"
        
        # Development/demo → Local FS
        if self.settings.is_development:
            if "local_fs" in available:
                return "local_fs"
        
        # Default to local for simplicity
        return "local_fs" if "local_fs" in available else available[0] if available else None
    
    def _llm_select(
        self,
        capability: str,
        context: dict[str, Any],
        available_tools: list[str],
    ) -> str | None:
        """
        LLM-based tool selection fallback.
        
        Uses Claude to select tool when rules are insufficient.
        """
        if not self.settings.anthropic_api_key:
            return None
        
        try:
            from langchain_anthropic import ChatAnthropic
            
            llm = ChatAnthropic(
                model=self.settings.anthropic_model,
                api_key=self.settings.anthropic_api_key,
                max_tokens=100,
            )
            
            prompt = f"""You are a tool selection agent. Select the best tool for this task.

Capability: {capability}
Available tools: {available_tools}
Context: {context}

Respond with ONLY the tool name, nothing else."""

            response = llm.invoke(prompt)
            selected = response.content.strip().lower()
            
            # Validate the selection
            if selected in available_tools:
                logger.debug(f"LLM selected tool: {selected}")
                return selected
            
            # Try to match partial names
            for tool in available_tools:
                if tool in selected or selected in tool:
                    return tool
            
        except Exception as e:
            logger.warning(f"LLM selection failed: {e}")
        
        return None
    
    def _get_default(self, capability: str) -> str:
        """Get default tool for capability."""
        # Try registry default first
        registry_default = self.registry.get_default_tool(capability)
        if registry_default:
            return registry_default
        
        # Fall back to config defaults
        return DEFAULT_TOOL_SELECTIONS.get(capability, "mock")
    
    def _log_selection(
        self,
        capability: str,
        selected: str,
        context: dict[str, Any],
        available: list[str],
    ) -> None:
        """Log tool selection for audit."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "capability": capability,
            "selected": selected,
            "context_keys": list(context.keys()),
            "available_tools": available,
            "selection_method": "rule_based",  # or "llm_fallback"
        }
        self._selection_log.append(log_entry)
        
        logger.debug(
            f"Bigtool selected: {selected} for {capability} "
            f"(from pool: {available})"
        )
    
    def get_selection_log(self) -> list[dict[str, Any]]:
        """Get all tool selections made."""
        return self._selection_log
    
    def clear_selection_log(self) -> None:
        """Clear selection log."""
        self._selection_log = []
    
    def get_tool_pool(self, capability: str) -> list[str]:
        """Get available tools for a capability."""
        return self.registry.list_tools(capability)
    
    def execute_tool(
        self,
        capability: str,
        context: dict[str, Any],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Select and execute a tool in one call.
        
        Args:
            capability: Tool capability
            context: Selection context
            params: Execution parameters
            
        Returns:
            Tool execution result
        """
        tool_name = self.select(capability, context)
        tool = self.registry.get_tool(capability, tool_name)
        
        if not tool:
            return {
                "success": False,
                "error": f"Tool not found: {tool_name}",
                "tool_name": tool_name,
            }
        
        result = tool.execute(params)
        return result.to_dict()


# ============================================
# SINGLETON INSTANCE
# ============================================

_picker: BigtoolPicker | None = None


def get_bigtool_picker() -> BigtoolPicker:
    """Get singleton BigtoolPicker instance."""
    global _picker
    if _picker is None:
        _picker = BigtoolPicker()
    return _picker


__all__ = ["BigtoolPicker", "get_bigtool_picker"]

