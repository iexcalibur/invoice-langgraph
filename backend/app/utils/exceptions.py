"""Custom exceptions for Invoice LangGraph Agent."""

from typing import Any


class InvoiceAgentError(Exception):
    """Base exception for all Invoice Agent errors."""
    
    def __init__(self, message: str, code: str = "INVOICE_AGENT_ERROR", details: dict[str, Any] | None = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


class WorkflowError(InvoiceAgentError):
    """Workflow-level errors."""
    
    def __init__(self, message: str, workflow_id: str | None = None, code: str = "WORKFLOW_ERROR", details: dict[str, Any] | None = None):
        details = details or {}
        if workflow_id:
            details["workflow_id"] = workflow_id
        super().__init__(message, code, details)
        self.workflow_id = workflow_id


class StageError(WorkflowError):
    """Stage execution errors."""
    
    def __init__(self, message: str, stage_id: str, workflow_id: str | None = None, code: str = "STAGE_ERROR", details: dict[str, Any] | None = None):
        details = details or {}
        details["stage_id"] = stage_id
        super().__init__(message, workflow_id, code, details)
        self.stage_id = stage_id


class CheckpointError(WorkflowError):
    """Checkpoint-related errors."""
    
    def __init__(self, message: str, checkpoint_id: str | None = None, workflow_id: str | None = None, code: str = "CHECKPOINT_ERROR", details: dict[str, Any] | None = None):
        details = details or {}
        if checkpoint_id:
            details["checkpoint_id"] = checkpoint_id
        super().__init__(message, workflow_id, code, details)
        self.checkpoint_id = checkpoint_id


class MCPError(InvoiceAgentError):
    """MCP client/server errors."""
    
    def __init__(self, message: str, server: str, ability: str | None = None, code: str = "MCP_ERROR", details: dict[str, Any] | None = None):
        details = details or {}
        details["server"] = server
        if ability:
            details["ability"] = ability
        super().__init__(message, code, details)
        self.server = server
        self.ability = ability


class BigtoolError(InvoiceAgentError):
    """Bigtool selection/execution errors."""
    
    def __init__(self, message: str, capability: str, code: str = "BIGTOOL_ERROR", details: dict[str, Any] | None = None):
        details = details or {}
        details["capability"] = capability
        super().__init__(message, code, details)
        self.capability = capability


class ValidationError(InvoiceAgentError):
    """Input validation errors."""
    
    def __init__(self, message: str, field: str | None = None, code: str = "VALIDATION_ERROR", details: dict[str, Any] | None = None):
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(message, code, details)
        self.field = field


class NotFoundError(InvoiceAgentError):
    """Resource not found errors."""
    
    def __init__(self, message: str, resource_type: str, resource_id: str, code: str = "NOT_FOUND", details: dict[str, Any] | None = None):
        details = details or {}
        details["resource_type"] = resource_type
        details["resource_id"] = resource_id
        super().__init__(message, code, details)
        self.resource_type = resource_type
        self.resource_id = resource_id
