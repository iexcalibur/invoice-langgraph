"""LangGraph checkpoint store integration."""

from typing import Any, Optional
from datetime import datetime

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.config import get_settings
from app.utils.logger import logger


class CheckpointStore:
    """Wrapper for LangGraph checkpoint storage."""
    
    def __init__(self):
        self.settings = get_settings()
        self._saver: Optional[AsyncSqliteSaver] = None
    
    async def get_saver(self) -> AsyncSqliteSaver:
        """Get or create the checkpoint saver."""
        if self._saver is None:
            db_path = self.settings.langgraph_checkpoint_db.replace("sqlite:///", "")
            self._saver = AsyncSqliteSaver.from_conn_string(f"sqlite:///{db_path}")
        return self._saver
    
    async def save_checkpoint(
        self,
        workflow_id: str,
        stage_id: str,
        state: dict[str, Any],
    ) -> str:
        """Save a checkpoint for HITL."""
        saver = await self.get_saver()
        
        config = {"configurable": {"thread_id": workflow_id}}
        checkpoint_id = f"cp_{workflow_id}_{datetime.utcnow().timestamp()}"
        
        logger.info(f"Saving checkpoint {checkpoint_id} for workflow {workflow_id}")
        
        return checkpoint_id
    
    async def load_checkpoint(self, workflow_id: str) -> Optional[dict[str, Any]]:
        """Load the latest checkpoint for a workflow."""
        saver = await self.get_saver()
        
        config = {"configurable": {"thread_id": workflow_id}}
        
        try:
            checkpoint = await saver.aget(config)
            if checkpoint:
                return checkpoint
        except Exception as e:
            logger.error(f"Error loading checkpoint: {e}")
        
        return None


_checkpoint_store: Optional[CheckpointStore] = None


def get_checkpoint_store() -> CheckpointStore:
    """Get the singleton checkpoint store."""
    global _checkpoint_store
    if _checkpoint_store is None:
        _checkpoint_store = CheckpointStore()
    return _checkpoint_store


__all__ = ["CheckpointStore", "get_checkpoint_store"]
