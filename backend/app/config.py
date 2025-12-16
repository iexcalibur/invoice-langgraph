"""
Configuration management for Invoice LangGraph Agent.

Handles:
- Environment variable loading via Pydantic Settings
- Workflow configuration from workflow.json
- Stage definitions and routing maps
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# ============================================
# BASE PATHS
# ============================================

BASE_DIR = Path(__file__).resolve().parent.parent
WORKFLOW_JSON_PATH = BASE_DIR / "workflow.json"


# ============================================
# APPLICATION SETTINGS
# ============================================

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # === Application ===
    app_name: str = Field(default="Invoice LangGraph Agent")
    app_env: str = Field(default="development")
    debug: bool = Field(default=True)
    
    # === API Server ===
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_reload: bool = Field(default=True)
    
    # === Database ===
    database_url: str = Field(default="sqlite:///./demo.db")
    
    # === LangGraph ===
    langgraph_checkpoint_db: str = Field(default="sqlite:///./demo.db")
    
    # === Claude API (Optional) ===
    anthropic_api_key: str | None = Field(default=None)
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022")
    
    # === Workflow Configuration ===
    match_threshold: float = Field(default=0.90)
    two_way_tolerance_pct: float = Field(default=5.0)
    human_review_queue: str = Field(default="human_review_queue")
    checkpoint_table: str = Field(default="checkpoints")
    
    # === CORS ===
    cors_origins: list[str] = Field(default=["http://localhost:3000"])
    
    # === Logging ===
    log_level: str = Field(default="DEBUG")
    log_format: str = Field(default="colored")
    
    # === Frontend URL ===
    frontend_url: str = Field(default="http://localhost:3000")
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @property
    def is_development(self) -> bool:
        return self.app_env.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


# ============================================
# WORKFLOW CONFIGURATION
# ============================================

class StageConfig:
    """Configuration for a single workflow stage."""
    
    def __init__(self, stage_data: dict[str, Any]):
        self.id: str = stage_data["id"]
        self.mode: str = stage_data["mode"]
        self.agent: str = stage_data["agent"]
        self.instructions: str = stage_data["instructions"]
        self.tools: list[dict] = stage_data.get("tools", [])
        self.output_schema: dict = stage_data.get("output_schema", {})
        self.trigger_condition: str | None = stage_data.get("trigger_condition")
    
    @property
    def is_deterministic(self) -> bool:
        return self.mode == "deterministic"
    
    @property
    def is_non_deterministic(self) -> bool:
        return self.mode == "non-deterministic"
    
    @property
    def bigtool_configs(self) -> list[dict]:
        return [t for t in self.tools if t.get("name") == "BigtoolPicker"]
    
    def __repr__(self) -> str:
        return f"StageConfig(id={self.id}, mode={self.mode})"


class WorkflowConfig:
    """Workflow configuration loaded from workflow.json."""
    
    def __init__(self, config_path: Path = WORKFLOW_JSON_PATH):
        self._config_path = config_path
        self._raw_config: dict[str, Any] = {}
        self._stages: dict[str, StageConfig] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        if not self._config_path.exists():
            # Use default config if file doesn't exist
            self._raw_config = self._get_default_config()
        else:
            with open(self._config_path, "r", encoding="utf-8") as f:
                self._raw_config = json.load(f)
        
        for stage_data in self._raw_config.get("stages", []):
            stage = StageConfig(stage_data)
            self._stages[stage.id] = stage
    
    def _get_default_config(self) -> dict[str, Any]:
        """Return default workflow configuration."""
        return {
            "version": "1.0",
            "workflow_name": "InvoiceProcessing_v1",
            "description": "LangGraph invoice processing with HITL",
            "config": {
                "match_threshold": 0.90,
                "two_way_tolerance_pct": 5,
            },
            "stages": [
                {"id": "INTAKE", "mode": "deterministic", "agent": "IngestNode", "instructions": "Validate and persist invoice"},
                {"id": "UNDERSTAND", "mode": "deterministic", "agent": "OcrNlpNode", "instructions": "OCR and parse invoice"},
                {"id": "PREPARE", "mode": "deterministic", "agent": "NormalizeEnrichNode", "instructions": "Normalize and enrich vendor"},
                {"id": "RETRIEVE", "mode": "deterministic", "agent": "ErpFetchNode", "instructions": "Fetch PO/GRN data"},
                {"id": "MATCH_TWO_WAY", "mode": "deterministic", "agent": "TwoWayMatcherNode", "instructions": "Compute match score"},
                {"id": "CHECKPOINT_HITL", "mode": "deterministic", "agent": "CheckpointNode", "instructions": "Create checkpoint for review"},
                {"id": "HITL_DECISION", "mode": "non-deterministic", "agent": "HumanReviewNode", "instructions": "Process human decision"},
                {"id": "RECONCILE", "mode": "deterministic", "agent": "ReconciliationNode", "instructions": "Build accounting entries"},
                {"id": "APPROVE", "mode": "deterministic", "agent": "ApprovalNode", "instructions": "Apply approval policy"},
                {"id": "POSTING", "mode": "deterministic", "agent": "PostingNode", "instructions": "Post to ERP"},
                {"id": "NOTIFY", "mode": "deterministic", "agent": "NotifyNode", "instructions": "Send notifications"},
                {"id": "COMPLETE", "mode": "deterministic", "agent": "CompleteNode", "instructions": "Finalize workflow"},
            ],
            "tools_hint": {
                "example_pools": {
                    "ocr": ["google_vision", "tesseract", "aws_textract"],
                    "enrichment": ["clearbit", "people_data_labs", "vendor_db"],
                    "erp_connector": ["sap_sandbox", "netsuite", "mock_erp"],
                    "db": ["postgres", "sqlite", "dynamodb"],
                    "email": ["sendgrid", "smartlead", "ses"],
                }
            }
        }
    
    @property
    def version(self) -> str:
        return self._raw_config.get("version", "1.0")
    
    @property
    def workflow_name(self) -> str:
        return self._raw_config.get("workflow_name", "InvoiceProcessing")
    
    @property
    def description(self) -> str:
        return self._raw_config.get("description", "")
    
    @property
    def config(self) -> dict[str, Any]:
        return self._raw_config.get("config", {})
    
    @property
    def match_threshold(self) -> float:
        return self.config.get("match_threshold", 0.90)
    
    @property
    def two_way_tolerance_pct(self) -> float:
        return self.config.get("two_way_tolerance_pct", 5.0)
    
    @property
    def stages(self) -> dict[str, StageConfig]:
        return self._stages
    
    @property
    def stage_order(self) -> list[str]:
        return [s["id"] for s in self._raw_config.get("stages", [])]
    
    @property
    def bigtool_pools(self) -> dict[str, list[str]]:
        return self._raw_config.get("tools_hint", {}).get("example_pools", {})
    
    def get_stage(self, stage_id: str) -> StageConfig | None:
        return self._stages.get(stage_id)
    
    def get_next_stage(self, current_stage_id: str) -> str | None:
        try:
            current_index = self.stage_order.index(current_stage_id)
            if current_index + 1 < len(self.stage_order):
                return self.stage_order[current_index + 1]
        except ValueError:
            pass
        return None


@lru_cache
def get_workflow_config() -> WorkflowConfig:
    return WorkflowConfig()


# ============================================
# MCP SERVER ROUTING
# ============================================

class MCPServerType:
    COMMON = "COMMON"
    ATLAS = "ATLAS"


MCP_ROUTING_TABLE: dict[str, str] = {
    # COMMON Server
    "validate_schema": MCPServerType.COMMON,
    "persist_raw_invoice": MCPServerType.COMMON,
    "parse_line_items": MCPServerType.COMMON,
    "normalize_vendor": MCPServerType.COMMON,
    "compute_flags": MCPServerType.COMMON,
    "compute_match_score": MCPServerType.COMMON,
    "save_checkpoint": MCPServerType.COMMON,
    "build_accounting_entries": MCPServerType.COMMON,
    "apply_approval_policy": MCPServerType.COMMON,
    "output_final_payload": MCPServerType.COMMON,
    # ATLAS Server
    "ocr_extract": MCPServerType.ATLAS,
    "enrich_vendor": MCPServerType.ATLAS,
    "fetch_po": MCPServerType.ATLAS,
    "fetch_grn": MCPServerType.ATLAS,
    "fetch_history": MCPServerType.ATLAS,
    "human_review_action": MCPServerType.ATLAS,
    "post_to_erp": MCPServerType.ATLAS,
    "schedule_payment": MCPServerType.ATLAS,
    "notify_vendor": MCPServerType.ATLAS,
    "notify_finance_team": MCPServerType.ATLAS,
}


def get_mcp_server(ability: str) -> str:
    return MCP_ROUTING_TABLE.get(ability, MCPServerType.COMMON)


# ============================================
# CONSTANTS
# ============================================

class StageID:
    INTAKE = "INTAKE"
    UNDERSTAND = "UNDERSTAND"
    PREPARE = "PREPARE"
    RETRIEVE = "RETRIEVE"
    MATCH_TWO_WAY = "MATCH_TWO_WAY"
    CHECKPOINT_HITL = "CHECKPOINT_HITL"
    HITL_DECISION = "HITL_DECISION"
    RECONCILE = "RECONCILE"
    APPROVE = "APPROVE"
    POSTING = "POSTING"
    NOTIFY = "NOTIFY"
    COMPLETE = "COMPLETE"


class WorkflowStatus:
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    MANUAL_HANDOFF = "MANUAL_HANDOFF"


class MatchResult:
    MATCHED = "MATCHED"
    FAILED = "FAILED"


class HumanDecisionType:
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"


class BigtoolCapability:
    OCR = "ocr"
    ENRICHMENT = "enrichment"
    ERP_CONNECTOR = "erp_connector"
    DB = "db"
    EMAIL = "email"
    STORAGE = "storage"


DEFAULT_TOOL_SELECTIONS: dict[str, str] = {
    BigtoolCapability.OCR: "google_vision",
    BigtoolCapability.ENRICHMENT: "clearbit",
    BigtoolCapability.ERP_CONNECTOR: "mock_erp",
    BigtoolCapability.DB: "sqlite",
    BigtoolCapability.EMAIL: "sendgrid",
    BigtoolCapability.STORAGE: "local_fs",
}
