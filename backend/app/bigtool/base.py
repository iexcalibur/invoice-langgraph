"""
BaseTool - Abstract base class for all Bigtool implementations.

All tool implementations (OCR, Enrichment, ERP, Storage, Email, DB) must inherit from this.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol, runtime_checkable


@dataclass
class ToolMetadata:
    """Metadata for a tool implementation."""
    
    name: str
    capability: str
    provider: str
    description: str = ""
    version: str = "1.0.0"
    is_mock: bool = True
    config: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "capability": self.capability,
            "provider": self.provider,
            "description": self.description,
            "version": self.version,
            "is_mock": self.is_mock,
        }


@dataclass
class ToolResult:
    """Result from a tool execution."""
    
    success: bool
    data: dict[str, Any]
    tool_name: str
    execution_time_ms: float = 0.0
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "tool_name": self.tool_name,
            "execution_time_ms": self.execution_time_ms,
            "error": self.error,
            "metadata": self.metadata,
        }


@runtime_checkable
class ToolProtocol(Protocol):
    """Protocol for tool implementations."""
    
    @property
    def metadata(self) -> ToolMetadata:
        """Return tool metadata."""
        ...
    
    def execute(self, params: dict[str, Any]) -> ToolResult:
        """Execute the tool with given parameters."""
        ...
    
    def health_check(self) -> bool:
        """Check if tool is healthy/available."""
        ...


class BaseTool(ABC):
    """
    Abstract base class for all tool implementations.
    
    Provides common functionality for:
    - Execution timing
    - Error handling
    - Health checks
    - Metadata management
    """
    
    def __init__(
        self,
        name: str,
        capability: str,
        provider: str,
        description: str = "",
        is_mock: bool = True,
        config: dict[str, Any] | None = None,
    ):
        self._metadata = ToolMetadata(
            name=name,
            capability=capability,
            provider=provider,
            description=description,
            is_mock=is_mock,
            config=config or {},
        )
        self._last_execution: datetime | None = None
        self._execution_count: int = 0
    
    @property
    def metadata(self) -> ToolMetadata:
        """Return tool metadata."""
        return self._metadata
    
    @property
    def name(self) -> str:
        """Return tool name."""
        return self._metadata.name
    
    @property
    def capability(self) -> str:
        """Return tool capability."""
        return self._metadata.capability
    
    @property
    def provider(self) -> str:
        """Return tool provider."""
        return self._metadata.provider
    
    def execute(self, params: dict[str, Any]) -> ToolResult:
        """
        Execute the tool with timing and error handling.
        
        Args:
            params: Tool execution parameters
            
        Returns:
            ToolResult with execution outcome
        """
        start_time = datetime.utcnow()
        
        try:
            # Call the implementation
            result_data = self._execute(params)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._last_execution = datetime.utcnow()
            self._execution_count += 1
            
            return ToolResult(
                success=True,
                data=result_data,
                tool_name=self.name,
                execution_time_ms=execution_time,
                metadata={
                    "provider": self.provider,
                    "capability": self.capability,
                    "execution_count": self._execution_count,
                },
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return ToolResult(
                success=False,
                data={},
                tool_name=self.name,
                execution_time_ms=execution_time,
                error=str(e),
                metadata={
                    "provider": self.provider,
                    "capability": self.capability,
                },
            )
    
    @abstractmethod
    def _execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Implementation-specific execution logic.
        
        Args:
            params: Tool execution parameters
            
        Returns:
            Result data dictionary
        """
        pass
    
    def health_check(self) -> bool:
        """
        Check if tool is healthy and available.
        
        Override in subclasses for real health checks.
        """
        return True
    
    def get_stats(self) -> dict[str, Any]:
        """Get tool execution statistics."""
        return {
            "name": self.name,
            "capability": self.capability,
            "provider": self.provider,
            "execution_count": self._execution_count,
            "last_execution": self._last_execution.isoformat() if self._last_execution else None,
            "is_healthy": self.health_check(),
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, provider={self.provider})"


# ============================================
# CAPABILITY-SPECIFIC BASE CLASSES
# ============================================

class BaseOCRTool(BaseTool):
    """Base class for OCR tools."""
    
    def __init__(
        self,
        name: str,
        provider: str,
        description: str = "",
        is_mock: bool = True,
        config: dict[str, Any] | None = None,
    ):
        super().__init__(
            name=name,
            capability="ocr",
            provider=provider,
            description=description or f"OCR tool using {provider}",
            is_mock=is_mock,
            config=config,
        )


class BaseEnrichmentTool(BaseTool):
    """Base class for enrichment tools."""
    
    def __init__(
        self,
        name: str,
        provider: str,
        description: str = "",
        is_mock: bool = True,
        config: dict[str, Any] | None = None,
    ):
        super().__init__(
            name=name,
            capability="enrichment",
            provider=provider,
            description=description or f"Enrichment tool using {provider}",
            is_mock=is_mock,
            config=config,
        )


class BaseERPConnector(BaseTool):
    """Base class for ERP connectors."""
    
    def __init__(
        self,
        name: str,
        provider: str,
        description: str = "",
        is_mock: bool = True,
        config: dict[str, Any] | None = None,
    ):
        super().__init__(
            name=name,
            capability="erp_connector",
            provider=provider,
            description=description or f"ERP connector for {provider}",
            is_mock=is_mock,
            config=config,
        )


class BaseStorageTool(BaseTool):
    """Base class for storage tools."""
    
    def __init__(
        self,
        name: str,
        provider: str,
        description: str = "",
        is_mock: bool = True,
        config: dict[str, Any] | None = None,
    ):
        super().__init__(
            name=name,
            capability="storage",
            provider=provider,
            description=description or f"Storage tool using {provider}",
            is_mock=is_mock,
            config=config,
        )


class BaseEmailTool(BaseTool):
    """Base class for email tools."""
    
    def __init__(
        self,
        name: str,
        provider: str,
        description: str = "",
        is_mock: bool = True,
        config: dict[str, Any] | None = None,
    ):
        super().__init__(
            name=name,
            capability="email",
            provider=provider,
            description=description or f"Email tool using {provider}",
            is_mock=is_mock,
            config=config,
        )


class BaseDBTool(BaseTool):
    """Base class for database tools."""
    
    def __init__(
        self,
        name: str,
        provider: str,
        description: str = "",
        is_mock: bool = True,
        config: dict[str, Any] | None = None,
    ):
        super().__init__(
            name=name,
            capability="db",
            provider=provider,
            description=description or f"Database tool using {provider}",
            is_mock=is_mock,
            config=config,
        )


__all__ = [
    "ToolMetadata",
    "ToolResult",
    "ToolProtocol",
    "BaseTool",
    "BaseOCRTool",
    "BaseEnrichmentTool",
    "BaseERPConnector",
    "BaseStorageTool",
    "BaseEmailTool",
    "BaseDBTool",
]

