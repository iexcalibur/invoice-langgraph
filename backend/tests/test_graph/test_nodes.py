"""
Tests for LangGraph node implementations.
"""

import pytest

from app.graph.state import InvoiceState, STAGE_OUTPUT_SCHEMAS
from app.config import StageID, MatchResult, WorkflowStatus


class TestInvoiceState:
    """Tests for InvoiceState TypedDict."""
    
    def test_state_has_all_stages(self):
        """Test state schema includes all stage outputs."""
        state_fields = InvoiceState.__annotations__.keys()
        
        # Core fields
        assert "workflow_id" in state_fields
        assert "invoice_id" in state_fields
        assert "status" in state_fields
        assert "current_stage" in state_fields
        
        # Stage outputs
        assert "raw_id" in state_fields  # INTAKE
        assert "parsed_invoice" in state_fields  # UNDERSTAND
        assert "vendor_profile" in state_fields  # PREPARE
        assert "matched_pos" in state_fields  # RETRIEVE
        assert "match_score" in state_fields  # MATCH_TWO_WAY
        assert "checkpoint_id" in state_fields  # CHECKPOINT_HITL
        assert "human_decision" in state_fields  # HITL_DECISION
        assert "accounting_entries" in state_fields  # RECONCILE
        assert "approval_status" in state_fields  # APPROVE
        assert "posted" in state_fields  # POSTING
        assert "notify_status" in state_fields  # NOTIFY
        assert "final_payload" in state_fields  # COMPLETE
    
    def test_state_output_schemas_defined(self):
        """Test output schemas are defined for all stages."""
        assert StageID.INTAKE in STAGE_OUTPUT_SCHEMAS
        assert StageID.UNDERSTAND in STAGE_OUTPUT_SCHEMAS
        assert StageID.PREPARE in STAGE_OUTPUT_SCHEMAS
        assert StageID.RETRIEVE in STAGE_OUTPUT_SCHEMAS
        assert StageID.MATCH_TWO_WAY in STAGE_OUTPUT_SCHEMAS
        assert StageID.CHECKPOINT_HITL in STAGE_OUTPUT_SCHEMAS
        assert StageID.HITL_DECISION in STAGE_OUTPUT_SCHEMAS
        assert StageID.RECONCILE in STAGE_OUTPUT_SCHEMAS
        assert StageID.APPROVE in STAGE_OUTPUT_SCHEMAS
        assert StageID.POSTING in STAGE_OUTPUT_SCHEMAS
        assert StageID.NOTIFY in STAGE_OUTPUT_SCHEMAS
        assert StageID.COMPLETE in STAGE_OUTPUT_SCHEMAS


class TestIntakeNode:
    """Tests for INTAKE node."""
    
    @pytest.mark.asyncio
    async def test_intake_node_execution(self, mock_workflow_state):
        """Test intake node processes invoice."""
        from app.graph.nodes import intake_node
        
        result = await intake_node(mock_workflow_state)
        
        assert "raw_id" in result
        assert "ingest_ts" in result
        assert "validated" in result
        assert result["current_stage"] == StageID.INTAKE
    
    @pytest.mark.asyncio
    async def test_intake_node_validates_payload(self, mock_workflow_state):
        """Test intake node validates payload."""
        from app.graph.nodes import intake_node
        
        result = await intake_node(mock_workflow_state)
        
        assert result["validated"] is True


class TestUnderstandNode:
    """Tests for UNDERSTAND node."""
    
    @pytest.mark.asyncio
    async def test_understand_node_execution(self, mock_workflow_state):
        """Test understand node processes OCR."""
        from app.graph.nodes import understand_node
        
        result = await understand_node(mock_workflow_state)
        
        assert "parsed_invoice" in result
        assert "ocr_provider_used" in result
        assert result["current_stage"] == StageID.UNDERSTAND
    
    @pytest.mark.asyncio
    async def test_understand_node_selects_ocr_tool(self, mock_workflow_state):
        """Test understand node selects OCR tool."""
        from app.graph.nodes import understand_node
        
        result = await understand_node(mock_workflow_state)
        
        assert result["ocr_provider_used"] in ["google_vision", "tesseract", "aws_textract"]


class TestMatchNode:
    """Tests for MATCH_TWO_WAY node."""
    
    @pytest.mark.asyncio
    async def test_match_node_execution(self, mock_workflow_state):
        """Test match node computes score."""
        from app.graph.nodes import match_node
        
        mock_workflow_state["matched_pos"] = [
            {"po_id": "PO-001", "amount": 10000.00}
        ]
        
        result = await match_node(mock_workflow_state)
        
        assert "match_score" in result
        assert "match_result" in result
        assert result["current_stage"] == StageID.MATCH_TWO_WAY
    
    @pytest.mark.asyncio
    async def test_match_node_matched_result(self, mock_workflow_state):
        """Test match node returns MATCHED when scores align."""
        from app.graph.nodes import match_node
        
        # Set up matching PO
        mock_workflow_state["matched_pos"] = [
            {"po_id": "PO-001", "amount": 10000.00}  # Same as invoice amount
        ]
        
        result = await match_node(mock_workflow_state)
        
        assert result["match_score"] >= 0.9
        assert result["match_result"] == MatchResult.MATCHED
    
    @pytest.mark.asyncio
    async def test_match_node_failed_result(self, mock_workflow_state):
        """Test match node returns FAILED when no POs."""
        from app.graph.nodes import match_node
        
        mock_workflow_state["matched_pos"] = []
        
        result = await match_node(mock_workflow_state)
        
        assert result["match_score"] < 0.9
        assert result["match_result"] == MatchResult.FAILED


class TestCheckpointNode:
    """Tests for CHECKPOINT_HITL node."""
    
    @pytest.mark.asyncio
    async def test_checkpoint_node_execution(self, mock_workflow_state):
        """Test checkpoint node creates checkpoint."""
        from app.graph.nodes import checkpoint_node
        
        mock_workflow_state["match_score"] = 0.5
        mock_workflow_state["match_result"] = MatchResult.FAILED
        
        result = await checkpoint_node(mock_workflow_state)
        
        assert "checkpoint_id" in result
        assert "review_url" in result
        assert "paused_reason" in result
        assert result["status"] == WorkflowStatus.PAUSED


class TestHITLDecisionNode:
    """Tests for HITL_DECISION node."""
    
    @pytest.mark.asyncio
    async def test_hitl_decision_accept(self, mock_workflow_state):
        """Test HITL decision with ACCEPT."""
        from app.graph.nodes import hitl_decision_node
        
        mock_workflow_state["human_decision"] = "ACCEPT"
        mock_workflow_state["reviewer_id"] = "reviewer_001"
        mock_workflow_state["checkpoint_id"] = "cp_test_123"
        
        result = await hitl_decision_node(mock_workflow_state)
        
        assert result["human_decision"] == "ACCEPT"
        assert result["next_stage"] == StageID.RECONCILE
        assert result["status"] == WorkflowStatus.RUNNING
    
    @pytest.mark.asyncio
    async def test_hitl_decision_reject(self, mock_workflow_state):
        """Test HITL decision with REJECT."""
        from app.graph.nodes import hitl_decision_node
        
        mock_workflow_state["human_decision"] = "REJECT"
        mock_workflow_state["reviewer_id"] = "reviewer_001"
        mock_workflow_state["checkpoint_id"] = "cp_test_123"
        
        result = await hitl_decision_node(mock_workflow_state)
        
        assert result["human_decision"] == "REJECT"
        assert result["next_stage"] == StageID.COMPLETE
        assert result["status"] == WorkflowStatus.MANUAL_HANDOFF

