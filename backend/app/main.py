"""
FastAPI Application Entry Point.

Invoice LangGraph Agent - Main Application
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings, get_workflow_config
from app.api.router import api_router
from app.db.database import init_db, close_db
from app.utils.logger import setup_logger, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    settings = get_settings()
    
    # === STARTUP ===
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {settings.app_name}")
    logger.info(f"📍 Environment: {settings.app_env}")
    logger.info(f"🔧 Debug Mode: {settings.debug}")
    logger.info("=" * 60)
    
    setup_logger(level=settings.log_level, format_type=settings.log_format)
    
    logger.info("📦 Initializing database...")
    await init_db()
    logger.info("✅ Database initialized")
    
    logger.info("📋 Loading workflow configuration...")
    workflow_config = get_workflow_config()
    logger.info(f"✅ Loaded workflow: {workflow_config.workflow_name} v{workflow_config.version}")
    logger.info(f"📊 Stages: {len(workflow_config.stages)}")
    
    app.state.settings = settings
    app.state.workflow_config = workflow_config
    app.state.start_time = datetime.utcnow()
    
    logger.info("🟢 Application started successfully")
    logger.info(f"🌐 API: http://{settings.api_host}:{settings.api_port}")
    logger.info(f"📚 Docs: http://{settings.api_host}:{settings.api_port}/docs")
    
    yield
    
    # === SHUTDOWN ===
    logger.info("🔴 Shutting down application...")
    await close_db()
    logger.info("✅ Database connections closed")
    logger.info("👋 Application shutdown complete")


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.app_name,
        description="""
## Invoice LangGraph Agent

A LangGraph-based invoice processing workflow with Human-in-the-Loop (HITL) support.

### Features
- **12-Stage Pipeline**: INTAKE → UNDERSTAND → PREPARE → RETRIEVE → MATCH → CHECKPOINT → HITL → RECONCILE → APPROVE → POSTING → NOTIFY → COMPLETE
- **HITL Checkpointing**: Pause workflow for human review, resume after decision
- **MCP Integration**: Route abilities to COMMON/ATLAS servers
- **Bigtool Selection**: Dynamic tool selection from pools
- **Real-time Logs**: Server-Sent Events for live monitoring
        """,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )
    
    register_exception_handlers(app)
    app.include_router(api_router, prefix="/api/v1")
    register_root_routes(app)
    
    return app


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers."""
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {"type": "validation_error", "message": "Request validation failed", "details": exc.errors()},
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {"type": "internal_error", "message": "An unexpected error occurred"},
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


def register_root_routes(app: FastAPI) -> None:
    """Register root-level routes."""
    
    @app.get("/", tags=["Root"])
    async def root() -> dict[str, Any]:
        settings = get_settings()
        return {
            "name": settings.app_name,
            "version": "1.0.0",
            "status": "operational",
            "docs": "/docs",
            "health": "/health",
        }
    
    @app.get("/health", tags=["Health"])
    async def health_check(request: Request) -> dict[str, Any]:
        settings = request.app.state.settings
        start_time = request.app.state.start_time
        uptime = (datetime.utcnow() - start_time).total_seconds()
        
        return {
            "status": "healthy",
            "environment": settings.app_env,
            "uptime_seconds": round(uptime, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "database": "connected",
                "langgraph": "ready",
                "mcp_common": "available",
                "mcp_atlas": "available",
            },
        }
    
    @app.get("/health/ready", tags=["Health"])
    async def readiness_check() -> dict[str, Any]:
        return {"ready": True, "timestamp": datetime.utcnow().isoformat()}
    
    @app.get("/health/live", tags=["Health"])
    async def liveness_check() -> dict[str, Any]:
        return {"alive": True, "timestamp": datetime.utcnow().isoformat()}
    
    @app.get("/config/workflow", tags=["Config"])
    async def get_workflow_info(request: Request) -> dict[str, Any]:
        workflow_config = request.app.state.workflow_config
        return {
            "name": workflow_config.workflow_name,
            "version": workflow_config.version,
            "description": workflow_config.description,
            "match_threshold": workflow_config.match_threshold,
            "stages": [{"id": s.id, "mode": s.mode, "agent": s.agent} for s in workflow_config.stages.values()],
            "bigtool_pools": workflow_config.bigtool_pools,
        }


app = create_application()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run("app.main:app", host=settings.api_host, port=settings.api_port, reload=settings.api_reload)
