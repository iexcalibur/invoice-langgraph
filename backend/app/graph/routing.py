"""Conditional routing functions for LangGraph workflow."""

from typing import Literal

from app.graph.state import InvoiceState
from app.config import MatchResult, HumanDecisionType, StageID


def route_after_match(state: InvoiceState) -> Literal["checkpoint", "reconcile"]:
    """
    Route after MATCH_TWO_WAY stage.
    
    If match failed -> go to checkpoint for human review
    If match succeeded -> go directly to reconcile
    """
    match_result = state.get("match_result")
    
    if match_result == MatchResult.FAILED:
        return "checkpoint"
    return "reconcile"


def route_after_hitl(state: InvoiceState) -> Literal["reconcile", "complete"]:
    """
    Route after HITL_DECISION stage.
    
    If human accepted -> continue to reconcile
    If human rejected -> go to complete with MANUAL_HANDOFF status
    """
    decision = state.get("human_decision")
    
    if decision == HumanDecisionType.ACCEPT:
        return "reconcile"
    return "complete"


def should_skip_checkpoint(state: InvoiceState) -> bool:
    """Check if checkpoint should be skipped (match succeeded)."""
    return state.get("match_result") == MatchResult.MATCHED


def get_next_stage(current_stage: str, state: InvoiceState) -> str | None:
    """Get the next stage based on current stage and state."""
    
    # Define stage transitions
    transitions = {
        StageID.INTAKE: StageID.UNDERSTAND,
        StageID.UNDERSTAND: StageID.PREPARE,
        StageID.PREPARE: StageID.RETRIEVE,
        StageID.RETRIEVE: StageID.MATCH_TWO_WAY,
        StageID.MATCH_TWO_WAY: None,  # Conditional
        StageID.CHECKPOINT_HITL: StageID.HITL_DECISION,
        StageID.HITL_DECISION: None,  # Conditional
        StageID.RECONCILE: StageID.APPROVE,
        StageID.APPROVE: StageID.POSTING,
        StageID.POSTING: StageID.NOTIFY,
        StageID.NOTIFY: StageID.COMPLETE,
        StageID.COMPLETE: None,  # End
    }
    
    # Handle conditional transitions
    if current_stage == StageID.MATCH_TWO_WAY:
        if state.get("match_result") == MatchResult.FAILED:
            return StageID.CHECKPOINT_HITL
        return StageID.RECONCILE
    
    if current_stage == StageID.HITL_DECISION:
        if state.get("human_decision") == HumanDecisionType.ACCEPT:
            return StageID.RECONCILE
        return StageID.COMPLETE
    
    return transitions.get(current_stage)
