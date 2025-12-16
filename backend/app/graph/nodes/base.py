"""Base node class for workflow stages."""

from abc import ABC, abstractmethod
from typing import Any
from datetime import datetime

from app.graph.state import InvoiceState
from app.utils.logger import get_workflow_logger
from app.mcp import get_mcp_router
from app.bigtool import get_bigtool_picker


class BaseNode(ABC):
    """Base class for all workflow nodes."""
    
    stage_id: str = "BASE"
    
    def __init__(self, state: InvoiceState):
        self.state = state
        self.workflow_id = state.get("workflow_id", "unknown")
        self.logger = get_workflow_logger(self.workflow_id)
        self.mcp = get_mcp_router()
        self.bigtool = get_bigtool_picker()
        self.start_time = datetime.utcnow()
    
    @abstractmethod
    async def execute(self) -> dict[str, Any]:
        """Execute the node logic. Must be implemented by subclasses."""
        pass
    
    async def __call__(self, state: InvoiceState) -> InvoiceState:
        """Node entry point called by LangGraph."""
        self.state = state
        self.workflow_id = state.get("workflow_id", "unknown")
        self.logger = get_workflow_logger(self.workflow_id)
        self.start_time = datetime.utcnow()
        
        self.logger.stage_start(self.stage_id)
        
        try:
            result = await self.execute()
            
            # Calculate duration
            duration_ms = (datetime.utcnow() - self.start_time).total_seconds() * 1000
            self.logger.stage_complete(self.stage_id, duration_ms=duration_ms)
            
            # Merge result into state
            new_state = {**state, **result, "current_stage": self.stage_id}
            return new_state
            
        except Exception as e:
            self.logger.stage_error(self.stage_id, str(e))
            raise
    
    def call_mcp(self, ability: str, params: dict[str, Any]) -> dict[str, Any]:
        """Call MCP ability and log it."""
        result = self.mcp.call(ability, params)
        return result
    
    def select_tool(self, capability: str, context: dict[str, Any] = None) -> str:
        """Select tool using Bigtool picker."""
        tool = self.bigtool.select(capability, context or {})
        return tool
