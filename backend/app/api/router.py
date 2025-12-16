"""
API Router - Aggregates all API routes.

This module registers all endpoint routers under the /api/v1 prefix.
Each router handles a specific resource domain.
"""

from fastapi import APIRouter

from app.api.invoke import router as invoke_router
from app.api.workflows import router as workflows_router
from app.api.human_review import router as human_review_router
from app.api.logs import router as logs_router


# ============================================
# MAIN API ROUTER
# ============================================

api_router = APIRouter()

# Register sub-routers with prefixes and tags
api_router.include_router(
    invoke_router,
    prefix="/invoke",
    tags=["Invoke"],
)

api_router.include_router(
    workflows_router,
    prefix="/workflows",
    tags=["Workflows"],
)

api_router.include_router(
    human_review_router,
    prefix="/human-review",
    tags=["Human Review"],
)

api_router.include_router(
    logs_router,
    prefix="/logs",
    tags=["Logs"],
)


# ============================================
# EXPORTS
# ============================================

__all__ = ["api_router"]
