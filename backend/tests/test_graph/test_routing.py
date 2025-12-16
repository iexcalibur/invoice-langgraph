"""
Tests for LangGraph routing logic.
"""

import pytest

from app.graph.routing import (
    route_after_match,
    route_after_hitl,
    should_skip_checkpoint,
    get_next_stage,
)
from app.config import StageID, MatchResult, HumanDecisionType


class TestRouteAfterMatch:
    """Tests for route_after_match function."""
    
    def test_route_to_checkpoint_on_failed(self):
        """Test routing to checkpoint when match fails."""
        state = {"match_result": MatchResult.FAILED}
        
        result = route_after_match(state)
        
        assert result == "checkpoint"
    
    def test_route_to_reconcile_on_matched(self):
        """Test routing to reconcile when match succeeds."""
        state = {"match_result": MatchResult.MATCHED}
        
        result = route_after_match(state)
        
        assert result == "reconcile"
    
    def test_route_to_reconcile_when_no_result(self):
        """Test routing to reconcile when no result (default)."""
        state = {}
        
        result = route_after_match(state)
        
        assert result == "reconcile"


class TestRouteAfterHITL:
    """Tests for route_after_hitl function."""
    
    def test_route_to_reconcile_on_accept(self):
        """Test routing to reconcile when human accepts."""
        state = {"human_decision": HumanDecisionType.ACCEPT}
        
        result = route_after_hitl(state)
        
        assert result == "reconcile"
    
    def test_route_to_complete_on_reject(self):
        """Test routing to complete when human rejects."""
        state = {"human_decision": HumanDecisionType.REJECT}
        
        result = route_after_hitl(state)
        
        assert result == "complete"
    
    def test_route_to_complete_when_no_decision(self):
        """Test routing to complete when no decision (default)."""
        state = {}
        
        result = route_after_hitl(state)
        
        assert result == "complete"


class TestShouldSkipCheckpoint:
    """Tests for should_skip_checkpoint function."""
    
    def test_skip_when_matched(self):
        """Test skip checkpoint when matched."""
        state = {"match_result": MatchResult.MATCHED}
        
        result = should_skip_checkpoint(state)
        
        assert result is True
    
    def test_no_skip_when_failed(self):
        """Test don't skip checkpoint when failed."""
        state = {"match_result": MatchResult.FAILED}
        
        result = should_skip_checkpoint(state)
        
        assert result is False


class TestGetNextStage:
    """Tests for get_next_stage function."""
    
    def test_sequential_transitions(self):
        """Test sequential stage transitions."""
        state = {}
        
        assert get_next_stage(StageID.INTAKE, state) == StageID.UNDERSTAND
        assert get_next_stage(StageID.UNDERSTAND, state) == StageID.PREPARE
        assert get_next_stage(StageID.PREPARE, state) == StageID.RETRIEVE
        assert get_next_stage(StageID.RETRIEVE, state) == StageID.MATCH_TWO_WAY
        assert get_next_stage(StageID.RECONCILE, state) == StageID.APPROVE
        assert get_next_stage(StageID.APPROVE, state) == StageID.POSTING
        assert get_next_stage(StageID.POSTING, state) == StageID.NOTIFY
        assert get_next_stage(StageID.NOTIFY, state) == StageID.COMPLETE
        assert get_next_stage(StageID.COMPLETE, state) is None
    
    def test_conditional_after_match_failed(self):
        """Test conditional transition after match fails."""
        state = {"match_result": MatchResult.FAILED}
        
        result = get_next_stage(StageID.MATCH_TWO_WAY, state)
        
        assert result == StageID.CHECKPOINT_HITL
    
    def test_conditional_after_match_success(self):
        """Test conditional transition after match succeeds."""
        state = {"match_result": MatchResult.MATCHED}
        
        result = get_next_stage(StageID.MATCH_TWO_WAY, state)
        
        assert result == StageID.RECONCILE
    
    def test_conditional_after_hitl_accept(self):
        """Test conditional transition after HITL accept."""
        state = {"human_decision": HumanDecisionType.ACCEPT}
        
        result = get_next_stage(StageID.HITL_DECISION, state)
        
        assert result == StageID.RECONCILE
    
    def test_conditional_after_hitl_reject(self):
        """Test conditional transition after HITL reject."""
        state = {"human_decision": HumanDecisionType.REJECT}
        
        result = get_next_stage(StageID.HITL_DECISION, state)
        
        assert result == StageID.COMPLETE

