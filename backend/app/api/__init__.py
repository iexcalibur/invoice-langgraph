"""
API module for Invoice LangGraph Agent.

This module contains all REST API endpoints organized by resource:
- invoke: Start invoice processing workflows
- workflows: Query and manage workflows
- human_review: HITL review queue and decisions
- logs: Real-time workflow logs via SSE
"""

from app.api.router import api_router

__all__ = ["api_router"]
