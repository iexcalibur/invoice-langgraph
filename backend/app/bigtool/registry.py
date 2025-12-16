"""
ToolRegistry - Register and discover tools for Bigtool selection.

Provides:
- Tool registration by capability
- Tool discovery and listing
- Tool retrieval by name
- Pool management for each capability
"""

from typing import Any
from datetime import datetime

from app.bigtool.base import BaseTool, ToolMetadata
from app.utils.logger import logger


class ToolRegistry:
    """
    Registry for all available tools.
    
    Manages tool pools for each capability (ocr, enrichment, erp_connector, etc.)
    """
    
    def __init__(self):
        # capability -> {tool_name -> tool_instance}
        self._tools: dict[str, dict[str, BaseTool]] = {}
        # Track registration order for default selection
        self._registration_order: dict[str, list[str]] = {}
        self._initialized = False
    
    def register(self, tool: BaseTool) -> None:
        """
        Register a tool in the registry.
        
        Args:
            tool: Tool instance to register
        """
        capability = tool.capability
        name = tool.name
        
        if capability not in self._tools:
            self._tools[capability] = {}
            self._registration_order[capability] = []
        
        if name in self._tools[capability]:
            logger.warning(f"Tool {name} already registered for {capability}, replacing")
        
        self._tools[capability][name] = tool
        if name not in self._registration_order[capability]:
            self._registration_order[capability].append(name)
        
        logger.debug(f"Registered tool: {name} for capability: {capability}")
    
    def unregister(self, capability: str, name: str) -> bool:
        """
        Unregister a tool from the registry.
        
        Args:
            capability: Tool capability
            name: Tool name
            
        Returns:
            True if tool was removed, False if not found
        """
        if capability in self._tools and name in self._tools[capability]:
            del self._tools[capability][name]
            if name in self._registration_order.get(capability, []):
                self._registration_order[capability].remove(name)
            return True
        return False
    
    def get_tool(self, capability: str, name: str) -> BaseTool | None:
        """
        Get a specific tool by capability and name.
        
        Args:
            capability: Tool capability (ocr, enrichment, etc.)
            name: Tool name (google_vision, clearbit, etc.)
            
        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(capability, {}).get(name)
    
    def get_tools(self, capability: str) -> dict[str, BaseTool]:
        """
        Get all tools for a capability.
        
        Args:
            capability: Tool capability
            
        Returns:
            Dictionary of tool_name -> tool_instance
        """
        return self._tools.get(capability, {})
    
    def list_tools(self, capability: str) -> list[str]:
        """
        List all tool names for a capability.
        
        Args:
            capability: Tool capability
            
        Returns:
            List of tool names
        """
        return list(self._tools.get(capability, {}).keys())
    
    def list_capabilities(self) -> list[str]:
        """
        List all registered capabilities.
        
        Returns:
            List of capability names
        """
        return list(self._tools.keys())
    
    def get_default_tool(self, capability: str) -> str | None:
        """
        Get the default (first registered) tool for a capability.
        
        Args:
            capability: Tool capability
            
        Returns:
            Default tool name or None
        """
        order = self._registration_order.get(capability, [])
        return order[0] if order else None
    
    def get_tool_metadata(self, capability: str, name: str) -> ToolMetadata | None:
        """
        Get metadata for a specific tool.
        
        Args:
            capability: Tool capability
            name: Tool name
            
        Returns:
            ToolMetadata or None
        """
        tool = self.get_tool(capability, name)
        return tool.metadata if tool else None
    
    def get_all_metadata(self) -> dict[str, list[dict[str, Any]]]:
        """
        Get metadata for all registered tools.
        
        Returns:
            Dictionary of capability -> list of tool metadata
        """
        result = {}
        for capability, tools in self._tools.items():
            result[capability] = [
                tool.metadata.to_dict() for tool in tools.values()
            ]
        return result
    
    def health_check_all(self) -> dict[str, dict[str, bool]]:
        """
        Run health checks on all registered tools.
        
        Returns:
            Dictionary of capability -> {tool_name -> is_healthy}
        """
        result = {}
        for capability, tools in self._tools.items():
            result[capability] = {
                name: tool.health_check() for name, tool in tools.items()
            }
        return result
    
    def get_healthy_tools(self, capability: str) -> list[str]:
        """
        Get list of healthy tools for a capability.
        
        Args:
            capability: Tool capability
            
        Returns:
            List of healthy tool names
        """
        tools = self._tools.get(capability, {})
        return [name for name, tool in tools.items() if tool.health_check()]
    
    def get_stats(self) -> dict[str, Any]:
        """Get registry statistics."""
        total_tools = sum(len(tools) for tools in self._tools.values())
        return {
            "total_capabilities": len(self._tools),
            "total_tools": total_tools,
            "capabilities": {
                cap: len(tools) for cap, tools in self._tools.items()
            },
            "tools_by_capability": {
                cap: list(tools.keys()) for cap, tools in self._tools.items()
            },
        }
    
    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()
        self._registration_order.clear()
        self._initialized = False
    
    def initialize_default_tools(self) -> None:
        """Initialize registry with default mock tools."""
        if self._initialized:
            return
        
        # Import and register default tools
        self._register_ocr_tools()
        self._register_enrichment_tools()
        self._register_erp_tools()
        self._register_storage_tools()
        self._register_email_tools()
        self._register_db_tools()
        
        self._initialized = True
        logger.info(f"ToolRegistry initialized with {self.get_stats()['total_tools']} tools")
    
    def _register_ocr_tools(self) -> None:
        """Register OCR tool implementations."""
        from app.bigtool.tools.ocr import (
            GoogleVisionOCR,
            TesseractOCR,
            AWSTextractOCR,
        )
        
        self.register(GoogleVisionOCR())
        self.register(TesseractOCR())
        self.register(AWSTextractOCR())
    
    def _register_enrichment_tools(self) -> None:
        """Register enrichment tool implementations."""
        from app.bigtool.tools.enrichment import (
            ClearbitEnrichment,
            PeopleDataLabsEnrichment,
            VendorDBEnrichment,
        )
        
        self.register(ClearbitEnrichment())
        self.register(PeopleDataLabsEnrichment())
        self.register(VendorDBEnrichment())
    
    def _register_erp_tools(self) -> None:
        """Register ERP connector implementations."""
        from app.bigtool.tools.erp import (
            SAPConnector,
            NetSuiteConnector,
            MockERPConnector,
        )
        
        self.register(SAPConnector())
        self.register(NetSuiteConnector())
        self.register(MockERPConnector())
    
    def _register_storage_tools(self) -> None:
        """Register storage tool implementations."""
        from app.bigtool.tools.storage import (
            S3Storage,
            GCSStorage,
            LocalFSStorage,
        )
        
        self.register(S3Storage())
        self.register(GCSStorage())
        self.register(LocalFSStorage())
    
    def _register_email_tools(self) -> None:
        """Register email tool implementations."""
        from app.bigtool.tools.email import (
            SendGridEmail,
            SESEmail,
            SMTPEmail,
        )
        
        self.register(SendGridEmail())
        self.register(SESEmail())
        self.register(SMTPEmail())
    
    def _register_db_tools(self) -> None:
        """Register database tool implementations."""
        from app.bigtool.tools.db import (
            PostgresTool,
            SQLiteTool,
            DynamoDBTool,
        )
        
        self.register(PostgresTool())
        self.register(SQLiteTool())
        self.register(DynamoDBTool())


# ============================================
# SINGLETON INSTANCE
# ============================================

_registry: ToolRegistry | None = None


def get_tool_registry() -> ToolRegistry:
    """Get singleton ToolRegistry instance."""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
        _registry.initialize_default_tools()
    return _registry


__all__ = ["ToolRegistry", "get_tool_registry"]

