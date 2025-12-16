"""
Tests for BigtoolPicker - Tool selection logic.
"""

import pytest

from app.bigtool import BigtoolPicker, ToolRegistry, get_bigtool_picker
from app.config import BigtoolCapability


class TestBigtoolPicker:
    """Tests for BigtoolPicker class."""
    
    def test_picker_initialization(self, tool_registry):
        """Test picker initializes correctly."""
        picker = BigtoolPicker(registry=tool_registry)
        
        assert picker.registry is not None
        assert picker.settings is not None
        assert picker._selection_log == []
    
    def test_select_ocr_default(self, bigtool_picker):
        """Test OCR tool selection with default context."""
        tool = bigtool_picker.select("ocr", {})
        
        assert tool is not None
        assert tool in ["google_vision", "tesseract", "aws_textract"]
    
    def test_select_ocr_high_quality(self, bigtool_picker):
        """Test OCR selection for high quality documents."""
        tool = bigtool_picker.select("ocr", {"quality": "high"})
        
        assert tool == "google_vision"
    
    def test_select_ocr_cost_sensitive(self, bigtool_picker):
        """Test OCR selection for cost-sensitive scenario."""
        tool = bigtool_picker.select("ocr", {"cost_sensitive": True})
        
        assert tool == "tesseract"
    
    def test_select_ocr_invoice_document(self, bigtool_picker):
        """Test OCR selection for invoice documents."""
        tool = bigtool_picker.select("ocr", {"document_type": "invoice"})
        
        assert tool == "google_vision"
    
    def test_select_enrichment_default(self, bigtool_picker):
        """Test enrichment tool selection with default context."""
        tool = bigtool_picker.select("enrichment", {})
        
        assert tool is not None
        assert tool in ["clearbit", "people_data_labs", "vendor_db"]
    
    def test_select_enrichment_known_vendor(self, bigtool_picker):
        """Test enrichment selection for known vendor."""
        tool = bigtool_picker.select("enrichment", {"is_known_vendor": True})
        
        assert tool == "vendor_db"
    
    def test_select_enrichment_b2b(self, bigtool_picker):
        """Test enrichment selection for B2B vendor."""
        tool = bigtool_picker.select("enrichment", {"vendor_type": "b2b"})
        
        assert tool == "clearbit"
    
    def test_select_erp_default(self, bigtool_picker):
        """Test ERP connector selection with default context."""
        tool = bigtool_picker.select("erp_connector", {})
        
        assert tool is not None
        assert tool in ["sap_sandbox", "netsuite", "mock_erp"]
    
    def test_select_erp_mock_for_development(self, bigtool_picker):
        """Test ERP selection uses mock in development."""
        tool = bigtool_picker.select("erp_connector", {"use_mock": True})
        
        assert tool == "mock_erp"
    
    def test_select_db_default(self, bigtool_picker):
        """Test database tool selection with default context."""
        tool = bigtool_picker.select("db", {})
        
        assert tool is not None
        assert tool in ["postgres", "sqlite", "dynamodb"]
    
    def test_select_db_sqlite_for_development(self, bigtool_picker):
        """Test database selection prefers SQLite in development."""
        tool = bigtool_picker.select("db", {})
        
        # In development mode, should prefer sqlite
        assert tool == "sqlite"
    
    def test_select_email_default(self, bigtool_picker):
        """Test email tool selection with default context."""
        tool = bigtool_picker.select("email", {})
        
        assert tool is not None
        assert tool in ["sendgrid", "ses", "smtp"]
    
    def test_select_email_high_volume(self, bigtool_picker):
        """Test email selection for high volume."""
        tool = bigtool_picker.select("email", {"volume": "high"})
        
        assert tool == "sendgrid"
    
    def test_select_storage_default(self, bigtool_picker):
        """Test storage tool selection with default context."""
        tool = bigtool_picker.select("storage", {})
        
        assert tool is not None
        assert tool in ["s3", "gcs", "local_fs"]
    
    def test_select_storage_local_for_development(self, bigtool_picker):
        """Test storage selection prefers local_fs in development."""
        tool = bigtool_picker.select("storage", {})
        
        assert tool == "local_fs"
    
    def test_selection_is_logged(self, bigtool_picker):
        """Test that selections are logged."""
        bigtool_picker.clear_selection_log()
        
        bigtool_picker.select("ocr", {"document_type": "invoice"})
        
        log = bigtool_picker.get_selection_log()
        assert len(log) == 1
        assert log[0]["capability"] == "ocr"
        assert log[0]["selected"] == "google_vision"
    
    def test_get_tool_pool(self, bigtool_picker):
        """Test getting available tools for capability."""
        pool = bigtool_picker.get_tool_pool("ocr")
        
        assert "google_vision" in pool
        assert "tesseract" in pool
        assert "aws_textract" in pool
    
    def test_unknown_capability_returns_default(self, bigtool_picker):
        """Test unknown capability returns default tool."""
        tool = bigtool_picker.select("unknown_capability", {})
        
        assert tool == "mock"


class TestToolRegistry:
    """Tests for ToolRegistry class."""
    
    def test_registry_initialization(self):
        """Test registry initializes correctly."""
        registry = ToolRegistry()
        
        assert registry._tools == {}
        assert registry._initialized is False
    
    def test_registry_initialize_default_tools(self):
        """Test registry loads default tools."""
        registry = ToolRegistry()
        registry.initialize_default_tools()
        
        assert registry._initialized is True
        assert len(registry.list_capabilities()) > 0
    
    def test_registry_list_tools(self, tool_registry):
        """Test listing tools for a capability."""
        tools = tool_registry.list_tools("ocr")
        
        assert len(tools) == 3
        assert "google_vision" in tools
        assert "tesseract" in tools
        assert "aws_textract" in tools
    
    def test_registry_get_tool(self, tool_registry):
        """Test getting a specific tool."""
        tool = tool_registry.get_tool("ocr", "google_vision")
        
        assert tool is not None
        assert tool.name == "google_vision"
        assert tool.capability == "ocr"
    
    def test_registry_get_tool_not_found(self, tool_registry):
        """Test getting non-existent tool returns None."""
        tool = tool_registry.get_tool("ocr", "nonexistent")
        
        assert tool is None
    
    def test_registry_get_default_tool(self, tool_registry):
        """Test getting default tool for capability."""
        default = tool_registry.get_default_tool("ocr")
        
        assert default is not None
        assert default in ["google_vision", "tesseract", "aws_textract"]
    
    def test_registry_list_capabilities(self, tool_registry):
        """Test listing all capabilities."""
        capabilities = tool_registry.list_capabilities()
        
        assert "ocr" in capabilities
        assert "enrichment" in capabilities
        assert "erp_connector" in capabilities
        assert "db" in capabilities
        assert "email" in capabilities
        assert "storage" in capabilities
    
    def test_registry_get_stats(self, tool_registry):
        """Test getting registry statistics."""
        stats = tool_registry.get_stats()
        
        assert "total_capabilities" in stats
        assert "total_tools" in stats
        assert stats["total_capabilities"] == 6
        assert stats["total_tools"] == 18  # 3 tools per capability × 6 capabilities


class TestToolExecution:
    """Tests for tool execution."""
    
    def test_tool_execute_returns_result(self, tool_registry):
        """Test tool execution returns proper result."""
        tool = tool_registry.get_tool("ocr", "google_vision")
        result = tool.execute({"attachments": ["test.pdf"]})
        
        assert result.success is True
        assert result.tool_name == "google_vision"
        assert "extracted_text" in result.data
        assert result.execution_time_ms > 0
    
    def test_tool_metadata(self, tool_registry):
        """Test tool metadata is accessible."""
        tool = tool_registry.get_tool("enrichment", "clearbit")
        
        assert tool.metadata.name == "clearbit"
        assert tool.metadata.capability == "enrichment"
        assert tool.metadata.provider == "Clearbit"
    
    def test_tool_health_check(self, tool_registry):
        """Test tool health check."""
        tool = tool_registry.get_tool("storage", "local_fs")
        
        assert tool.health_check() is True


class TestSingletonAccessors:
    """Tests for singleton accessor functions."""
    
    def test_get_bigtool_picker_singleton(self):
        """Test get_bigtool_picker returns singleton."""
        picker1 = get_bigtool_picker()
        picker2 = get_bigtool_picker()
        
        assert picker1 is picker2
    
    def test_picker_has_registry(self):
        """Test picker has initialized registry."""
        picker = get_bigtool_picker()
        
        assert picker.registry is not None
        assert picker.registry._initialized is True

