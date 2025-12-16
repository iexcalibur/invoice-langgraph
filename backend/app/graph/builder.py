"""LangGraph workflow builder."""

from functools import lru_cache
from typing import Any

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.config import get_settings, StageID
from app.graph.state import InvoiceState
from app.graph.routing import route_after_match, route_after_hitl
from app.graph.nodes import (
    intake_node,
    understand_node,
    prepare_node,
    retrieve_node,
    match_node,
    checkpoint_node,
    hitl_decision_node,
    reconcile_node,
    approve_node,
    posting_node,
    notify_node,
    complete_node,
)


def build_invoice_graph() -> StateGraph:
    """
    Build the LangGraph workflow for invoice processing.
    
    Returns:
        StateGraph: Compiled workflow graph
    """
    
    # Create graph with InvoiceState schema
    workflow = StateGraph(InvoiceState)
    
    # === Add all nodes ===
    workflow.add_node(StageID.INTAKE, intake_node)
    workflow.add_node(StageID.UNDERSTAND, understand_node)
    workflow.add_node(StageID.PREPARE, prepare_node)
    workflow.add_node(StageID.RETRIEVE, retrieve_node)
    workflow.add_node(StageID.MATCH_TWO_WAY, match_node)
    workflow.add_node(StageID.CHECKPOINT_HITL, checkpoint_node)
    workflow.add_node(StageID.HITL_DECISION, hitl_decision_node)
    workflow.add_node(StageID.RECONCILE, reconcile_node)
    workflow.add_node(StageID.APPROVE, approve_node)
    workflow.add_node(StageID.POSTING, posting_node)
    workflow.add_node(StageID.NOTIFY, notify_node)
    workflow.add_node(StageID.COMPLETE, complete_node)
    
    # === Define edges (sequential flow) ===
    workflow.set_entry_point(StageID.INTAKE)
    
    workflow.add_edge(StageID.INTAKE, StageID.UNDERSTAND)
    workflow.add_edge(StageID.UNDERSTAND, StageID.PREPARE)
    workflow.add_edge(StageID.PREPARE, StageID.RETRIEVE)
    workflow.add_edge(StageID.RETRIEVE, StageID.MATCH_TWO_WAY)
    
    # === Conditional edge after matching ===
    workflow.add_conditional_edges(
        StageID.MATCH_TWO_WAY,
        route_after_match,
        {
            "checkpoint": StageID.CHECKPOINT_HITL,
            "reconcile": StageID.RECONCILE,
        }
    )
    
    workflow.add_edge(StageID.CHECKPOINT_HITL, StageID.HITL_DECISION)
    
    # === Conditional edge after HITL decision ===
    workflow.add_conditional_edges(
        StageID.HITL_DECISION,
        route_after_hitl,
        {
            "reconcile": StageID.RECONCILE,
            "complete": StageID.COMPLETE,
        }
    )
    
    # === Continue sequential flow ===
    workflow.add_edge(StageID.RECONCILE, StageID.APPROVE)
    workflow.add_edge(StageID.APPROVE, StageID.POSTING)
    workflow.add_edge(StageID.POSTING, StageID.NOTIFY)
    workflow.add_edge(StageID.NOTIFY, StageID.COMPLETE)
    workflow.add_edge(StageID.COMPLETE, END)
    
    return workflow


@lru_cache
def get_workflow_graph():
    """
    Get compiled workflow graph with checkpointing.
    
    Returns:
        CompiledGraph: Ready-to-use workflow graph
    """
    settings = get_settings()
    
    # Build the graph
    graph = build_invoice_graph()
    
    # Create checkpointer for state persistence
    db_path = settings.langgraph_checkpoint_db.replace("sqlite:///", "")
    checkpointer = AsyncSqliteSaver.from_conn_string(f"sqlite:///{db_path}")
    
    # Compile with checkpointer
    return graph.compile(checkpointer=checkpointer)


def get_graph_visualization() -> str:
    """
    Get Mermaid diagram of the workflow graph.
    
    Returns:
        str: Mermaid diagram string
    """
    graph = build_invoice_graph()
    return graph.get_graph().draw_mermaid()
