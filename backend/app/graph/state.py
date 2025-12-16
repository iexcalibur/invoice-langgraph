"""InvoiceState TypedDict for LangGraph workflow."""

from typing import TypedDict, Literal, Any


class InvoiceState(TypedDict, total=False):
    """
    State schema for Invoice Processing workflow.
    
    This TypedDict defines all state variables passed between nodes.
    """
    
    # === Workflow Metadata ===
    workflow_id: str
    invoice_id: str
    current_stage: str
    status: Literal["PENDING", "RUNNING", "PAUSED", "COMPLETED", "FAILED", "MANUAL_HANDOFF"]
    started_at: str
    updated_at: str
    
    # === Raw Input ===
    raw_payload: dict[str, Any]
    
    # === INTAKE Outputs ===
    raw_id: str
    ingest_ts: str
    validated: bool
    storage_provider_used: str
    
    # === UNDERSTAND Outputs ===
    parsed_invoice: dict[str, Any]
    ocr_provider_used: str
    invoice_text: str
    parsed_line_items: list[dict[str, Any]]
    detected_pos: list[str]
    parsed_dates: dict[str, str]
    
    # === PREPARE Outputs ===
    vendor_profile: dict[str, Any]
    normalized_invoice: dict[str, Any]
    flags: dict[str, Any]
    enrichment_provider_used: str
    normalized_name: str
    risk_score: float
    missing_info: list[str]
    
    # === RETRIEVE Outputs ===
    matched_pos: list[dict[str, Any]]
    matched_grns: list[dict[str, Any]]
    history: list[dict[str, Any]]
    erp_connector_used: str
    
    # === MATCH_TWO_WAY Outputs ===
    match_score: float
    match_result: Literal["MATCHED", "FAILED"]
    tolerance_pct: float
    match_evidence: dict[str, Any]
    
    # === CHECKPOINT_HITL Outputs ===
    checkpoint_id: str | None
    review_url: str | None
    paused_reason: str | None
    
    # === HITL_DECISION Outputs ===
    human_decision: Literal["ACCEPT", "REJECT"] | None
    reviewer_id: str | None
    reviewer_notes: str | None
    resume_token: str | None
    next_stage: str | None
    
    # === RECONCILE Outputs ===
    accounting_entries: list[dict[str, Any]]
    reconciliation_report: dict[str, Any]
    
    # === APPROVE Outputs ===
    approval_status: Literal["AUTO_APPROVED", "ESCALATED", "APPROVED", "REJECTED"]
    approver_id: str | None
    
    # === POSTING Outputs ===
    posted: bool
    erp_txn_id: str | None
    scheduled_payment_id: str | None
    
    # === NOTIFY Outputs ===
    notify_status: dict[str, Any]
    notified_parties: list[str]
    email_provider_used: str
    
    # === COMPLETE Outputs ===
    final_payload: dict[str, Any]
    audit_log: list[dict[str, Any]]
    
    # === Error Tracking ===
    errors: list[dict[str, Any]]
    retry_count: int


# Stage output schemas for validation
STAGE_OUTPUT_SCHEMAS = {
    "INTAKE": {
        "raw_id": str,
        "ingest_ts": str,
        "validated": bool,
    },
    "UNDERSTAND": {
        "parsed_invoice": dict,
        "ocr_provider_used": str,
    },
    "PREPARE": {
        "vendor_profile": dict,
        "normalized_invoice": dict,
        "flags": dict,
    },
    "RETRIEVE": {
        "matched_pos": list,
        "matched_grns": list,
        "history": list,
    },
    "MATCH_TWO_WAY": {
        "match_score": float,
        "match_result": str,
        "tolerance_pct": float,
        "match_evidence": dict,
    },
    "CHECKPOINT_HITL": {
        "checkpoint_id": str,
        "review_url": str,
        "paused_reason": str,
    },
    "HITL_DECISION": {
        "human_decision": str,
        "reviewer_id": str,
        "next_stage": str,
    },
    "RECONCILE": {
        "accounting_entries": list,
        "reconciliation_report": dict,
    },
    "APPROVE": {
        "approval_status": str,
        "approver_id": str,
    },
    "POSTING": {
        "posted": bool,
        "erp_txn_id": str,
        "scheduled_payment_id": str,
    },
    "NOTIFY": {
        "notify_status": dict,
        "notified_parties": list,
    },
    "COMPLETE": {
        "final_payload": dict,
        "audit_log": list,
        "status": str,
    },
}
