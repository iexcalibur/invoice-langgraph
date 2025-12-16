"""MCP Router - Routes abilities to COMMON/ATLAS servers."""

from typing import Any
from datetime import datetime

from app.config import MCPServerType, MCP_ROUTING_TABLE
from app.mcp.common_server import CommonServer
from app.mcp.atlas_server import AtlasServer
from app.utils.logger import logger


class MCPRouter:
    """
    Routes MCP abilities to appropriate servers.
    
    COMMON Server: Internal operations (no external dependencies)
    ATLAS Server: External integrations (ERP, enrichment, notifications)
    """
    
    def __init__(self):
        self.common = CommonServer()
        self.atlas = AtlasServer()
        self._call_log: list[dict[str, Any]] = []
    
    def call(self, ability: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Route ability to appropriate server and execute.
        
        Args:
            ability: Ability name
            params: Ability parameters
            
        Returns:
            Ability execution result
        """
        server = self._get_server(ability)
        
        # Log the call
        call_record = {
            "ability": ability,
            "server": server,
            "timestamp": datetime.utcnow().isoformat(),
            "params_keys": list(params.keys()),
        }
        self._call_log.append(call_record)
        
        logger.debug(f"MCP [{server}] → {ability}")
        
        # Route to server
        if server == MCPServerType.COMMON:
            return self.common.execute(ability, params)
        else:
            return self.atlas.execute(ability, params)
    
    def _get_server(self, ability: str) -> str:
        """Get server type for ability."""
        return MCP_ROUTING_TABLE.get(ability, MCPServerType.COMMON)
    
    def get_call_log(self) -> list[dict[str, Any]]:
        """Get all MCP calls made."""
        return self._call_log
    
    def clear_call_log(self) -> None:
        """Clear call log."""
        self._call_log = []


_mcp_router: MCPRouter | None = None


def get_mcp_router() -> MCPRouter:
    """Get singleton MCP router instance."""
    global _mcp_router
    if _mcp_router is None:
        _mcp_router = MCPRouter()
    return _mcp_router
