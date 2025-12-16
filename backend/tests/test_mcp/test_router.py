"""
Tests for MCP Router - ability routing to COMMON/ATLAS servers.
"""

import pytest

from app.mcp import MCPRouter, get_mcp_router
from app.mcp.common_server import CommonServer
from app.mcp.atlas_server import AtlasServer
from app.config import MCPServerType, MCP_ROUTING_TABLE


class TestMCPRouter:
    """Tests for MCPRouter class."""
    
    def test_router_initialization(self, mcp_router):
        """Test router initializes correctly."""
        assert mcp_router.common is not None
        assert mcp_router.atlas is not None
        assert isinstance(mcp_router.common, CommonServer)
        assert isinstance(mcp_router.atlas, AtlasServer)
    
    def test_router_routes_to_common(self, mcp_router):
        """Test router routes COMMON abilities correctly."""
        # validate_schema should go to COMMON
        result = mcp_router.call("validate_schema", {"payload": {}})
        
        assert result is not None
        assert "valid" in result or "error" not in result
    
    def test_router_routes_to_atlas(self, mcp_router):
        """Test router routes ATLAS abilities correctly."""
        # ocr_extract should go to ATLAS
        result = mcp_router.call("ocr_extract", {"attachments": []})
        
        assert result is not None
        assert "extracted_text" in result or "error" not in result
    
    def test_router_logs_calls(self, mcp_router):
        """Test router logs all calls."""
        mcp_router.clear_call_log()
        
        mcp_router.call("validate_schema", {"payload": {}})
        mcp_router.call("ocr_extract", {"attachments": []})
        
        log = mcp_router.get_call_log()
        
        assert len(log) == 2
        assert log[0]["ability"] == "validate_schema"
        assert log[1]["ability"] == "ocr_extract"
    
    def test_router_handles_unknown_ability(self, mcp_router):
        """Test router handles unknown abilities gracefully."""
        result = mcp_router.call("unknown_ability", {})
        
        # Should return error or handle gracefully
        assert result is not None


class TestMCPRoutingTable:
    """Tests for MCP routing configuration."""
    
    def test_common_abilities_configured(self):
        """Test COMMON abilities are in routing table."""
        common_abilities = [
            "validate_schema",
            "persist_raw_invoice",
            "parse_line_items",
            "normalize_vendor",
            "compute_flags",
            "compute_match_score",
            "save_checkpoint",
            "build_accounting_entries",
            "apply_approval_policy",
            "output_final_payload",
        ]
        
        for ability in common_abilities:
            assert ability in MCP_ROUTING_TABLE
            assert MCP_ROUTING_TABLE[ability] == MCPServerType.COMMON
    
    def test_atlas_abilities_configured(self):
        """Test ATLAS abilities are in routing table."""
        atlas_abilities = [
            "ocr_extract",
            "enrich_vendor",
            "fetch_po",
            "fetch_grn",
            "fetch_history",
            "human_review_action",
            "post_to_erp",
            "schedule_payment",
            "notify_vendor",
            "notify_finance_team",
        ]
        
        for ability in atlas_abilities:
            assert ability in MCP_ROUTING_TABLE
            assert MCP_ROUTING_TABLE[ability] == MCPServerType.ATLAS


class TestCommonServer:
    """Tests for COMMON server abilities."""
    
    def test_validate_schema(self):
        """Test validate_schema ability."""
        server = CommonServer()
        
        result = server.execute("validate_schema", {
            "payload": {
                "invoice_id": "INV-001",
                "vendor_name": "Test Vendor",
                "amount": 1000,
            }
        })
        
        assert result["valid"] is True
        assert result["missing_fields"] == []
    
    def test_validate_schema_missing_fields(self):
        """Test validate_schema with missing fields."""
        server = CommonServer()
        
        result = server.execute("validate_schema", {"payload": {}})
        
        assert result["valid"] is False
        assert len(result["missing_fields"]) > 0
    
    def test_normalize_vendor(self):
        """Test normalize_vendor ability."""
        server = CommonServer()
        
        result = server.execute("normalize_vendor", {"vendor_name": "  Test  Vendor  "})
        
        assert result["normalized_name"] == "TEST VENDOR"
    
    def test_compute_match_score(self):
        """Test compute_match_score ability."""
        server = CommonServer()
        
        result = server.execute("compute_match_score", {
            "invoice_amount": 10000,
            "purchase_orders": [{"amount": 10000}],
            "threshold": 0.9,
            "tolerance_pct": 5,
        })
        
        assert "score" in result
        assert "matched" in result
        assert result["score"] >= 0.9  # Should match


class TestAtlasServer:
    """Tests for ATLAS server abilities."""
    
    def test_ocr_extract(self):
        """Test ocr_extract ability."""
        server = AtlasServer()
        
        result = server.execute("ocr_extract", {
            "attachments": ["invoice.pdf"],
            "provider": "google_vision",
        })
        
        assert "extracted_text" in result
        assert "confidence" in result
        assert result["provider"] == "google_vision"
    
    def test_enrich_vendor(self):
        """Test enrich_vendor ability."""
        server = AtlasServer()
        
        result = server.execute("enrich_vendor", {
            "vendor_name": "Test Corp",
            "provider": "clearbit",
        })
        
        assert result["enriched"] is True
        assert "data" in result
    
    def test_fetch_po(self):
        """Test fetch_po ability."""
        server = AtlasServer()
        
        result = server.execute("fetch_po", {
            "vendor_name": "Test Vendor",
            "po_numbers": ["PO-001"],
            "connector": "mock_erp",
        })
        
        assert "purchase_orders" in result
        assert len(result["purchase_orders"]) > 0
    
    def test_post_to_erp(self):
        """Test post_to_erp ability."""
        server = AtlasServer()
        
        result = server.execute("post_to_erp", {
            "entries": [{"debit": 1000, "credit": 1000}],
            "connector": "mock_erp",
        })
        
        assert result["posted"] is True
        assert "transaction_id" in result
    
    def test_notify_vendor(self):
        """Test notify_vendor ability."""
        server = AtlasServer()
        
        result = server.execute("notify_vendor", {
            "vendor_name": "Test Vendor",
            "invoice_id": "INV-001",
            "provider": "sendgrid",
        })
        
        assert result["sent"] is True


class TestSingletonAccessor:
    """Tests for singleton accessor."""
    
    def test_get_mcp_router_singleton(self):
        """Test get_mcp_router returns singleton."""
        router1 = get_mcp_router()
        router2 = get_mcp_router()
        
        assert router1 is router2

