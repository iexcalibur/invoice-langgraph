"""Logging configuration using Loguru."""

import sys
from typing import Literal
from datetime import datetime

from loguru import logger


def setup_logger(level: str = "DEBUG", format_type: Literal["colored", "json"] = "colored") -> None:
    """Configure Loguru logger."""
    logger.remove()
    
    if format_type == "json":
        logger.add(sys.stdout, level=level.upper(), format="{message}", serialize=True)
    else:
        logger.add(
            sys.stdout,
            level=level.upper(),
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            colorize=True,
        )


class WorkflowLogger:
    """Specialized logger for workflow execution."""
    
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self._logger = logger.bind(workflow_id=workflow_id)
    
    def stage_start(self, stage_id: str, **kwargs) -> None:
        self._logger.info(f"▶️  Stage [{stage_id}] started", stage_id=stage_id, event="stage_start", **kwargs)
    
    def stage_complete(self, stage_id: str, duration_ms: float = None, **kwargs) -> None:
        msg = f"✅ Stage [{stage_id}] completed"
        if duration_ms:
            msg += f" ({duration_ms:.2f}ms)"
        self._logger.info(msg, stage_id=stage_id, event="stage_complete", duration_ms=duration_ms, **kwargs)
    
    def stage_error(self, stage_id: str, error: str, **kwargs) -> None:
        self._logger.error(f"❌ Stage [{stage_id}] failed: {error}", stage_id=stage_id, event="stage_error", **kwargs)
    
    def bigtool_selection(self, capability: str, selected_tool: str, available_tools: list[str], **kwargs) -> None:
        self._logger.info(
            f"🔧 Bigtool selected [{selected_tool}] for [{capability}]",
            event="bigtool_selection", capability=capability, selected_tool=selected_tool, **kwargs
        )
    
    def mcp_call(self, server: str, ability: str, **kwargs) -> None:
        self._logger.info(f"📡 MCP [{server}] → {ability}", event="mcp_call", server=server, ability=ability, **kwargs)
    
    def checkpoint_created(self, checkpoint_id: str, reason: str, **kwargs) -> None:
        self._logger.warning(f"⏸️  Checkpoint: {checkpoint_id} | Reason: {reason}", event="checkpoint_created", **kwargs)
    
    def workflow_resumed(self, checkpoint_id: str, decision: str, **kwargs) -> None:
        self._logger.info(f"▶️  Resumed from {checkpoint_id} | Decision: {decision}", event="workflow_resumed", **kwargs)
    
    def workflow_complete(self, status: str, **kwargs) -> None:
        emoji = "🎉" if status == "COMPLETED" else "⚠️"
        self._logger.info(f"{emoji} Workflow completed: {status}", event="workflow_complete", status=status, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        self._logger.info(message, **kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        self._logger.debug(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        self._logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        self._logger.error(message, **kwargs)


def get_workflow_logger(workflow_id: str) -> WorkflowLogger:
    return WorkflowLogger(workflow_id)


__all__ = ["logger", "setup_logger", "WorkflowLogger", "get_workflow_logger"]
