"""COMMON Server - Internal operations (no external dependencies)."""

from typing import Any
from datetime import datetime

from app.utils.logger import logger


class CommonServer:
    """
    COMMON MCP Server - Handles internal operations.
    
    Abilities:
    - validate_schema
    - persist_raw_invoice
    - parse_line_items
    - normalize_vendor
    - compute_flags
    - compute_match_score
    - save_checkpoint
    - build_accounting_entries
    - apply_approval_policy
    - output_final_payload
    """
    
    def execute(self, ability: str, params: dict[str, Any]) -> dict[str, Any]:
        """Execute COMMON server ability."""
        handlers = {
            "validate_schema": self._validate_schema,
            "persist_raw_invoice": self._persist_raw_invoice,
            "parse_line_items": self._parse_line_items,
            "normalize_vendor": self._normalize_vendor,
            "compute_flags": self._compute_flags,
            "compute_match_score": self._compute_match_score,
            "save_checkpoint": self._save_checkpoint,
            "build_accounting_entries": self._build_accounting_entries,
            "apply_approval_policy": self._apply_approval_policy,
            "output_final_payload": self._output_final_payload,
        }
        
        handler = handlers.get(ability)
        if not handler:
            logger.warning(f"Unknown COMMON ability: {ability}")
            return {"error": f"Unknown ability: {ability}"}
        
        return handler(params)
    
    def _validate_schema(self, params: dict[str, Any]) -> dict[str, Any]:
        """Validate invoice payload schema."""
        payload = params.get("payload", {})
        required_fields = ["invoice_id", "vendor_name", "amount"]
        missing = [f for f in required_fields if f not in payload]
        
        return {
            "valid": len(missing) == 0,
            "missing_fields": missing,
            "validated_at": datetime.utcnow().isoformat(),
        }
    
    def _persist_raw_invoice(self, params: dict[str, Any]) -> dict[str, Any]:
        """Persist raw invoice (mock)."""
        return {
            "persisted": True,
            "raw_id": params.get("raw_id"),
            "storage": params.get("storage", "local_fs"),
        }
    
    def _parse_line_items(self, params: dict[str, Any]) -> dict[str, Any]:
        """Parse line items from text."""
        raw_payload = params.get("raw_payload", {})
        line_items = raw_payload.get("line_items", [])
        
        # Extract PO numbers from text (mock)
        text = params.get("text", "")
        detected_pos = []
        if "PO" in text.upper():
            detected_pos = ["PO-2024-001"]
        
        return {
            "line_items": line_items,
            "detected_pos": detected_pos,
            "parsed_at": datetime.utcnow().isoformat(),
        }
    
    def _normalize_vendor(self, params: dict[str, Any]) -> dict[str, Any]:
        """Normalize vendor name."""
        vendor_name = params.get("vendor_name", "")
        
        # Simple normalization
        normalized = vendor_name.strip().upper()
        normalized = " ".join(normalized.split())
        
        return {
            "original_name": vendor_name,
            "normalized_name": normalized,
        }
    
    def _compute_flags(self, params: dict[str, Any]) -> dict[str, Any]:
        """Compute validation flags."""
        vendor_profile = params.get("vendor_profile", {})
        invoice = params.get("invoice", {})
        
        missing_info = []
        if not invoice.get("vendor_tax_id"):
            missing_info.append("vendor_tax_id")
        if not invoice.get("due_date"):
            missing_info.append("due_date")
        
        # Simple risk score calculation
        risk_score = 0.0
        if missing_info:
            risk_score += 0.2 * len(missing_info)
        if invoice.get("amount", 0) > 50000:
            risk_score += 0.3
        
        return {
            "missing_info": missing_info,
            "risk_score": min(risk_score, 1.0),
        }
    
    def _compute_match_score(self, params: dict[str, Any]) -> dict[str, Any]:
        """Compute two-way match score."""
        invoice_amount = params.get("invoice_amount", 0)
        purchase_orders = params.get("purchase_orders", [])
        threshold = params.get("threshold", 0.9)
        tolerance_pct = params.get("tolerance_pct", 5)
        
        if not purchase_orders:
            return {"score": 0.0, "matched": False, "reason": "No POs found"}
        
        po_total = sum(po.get("amount", 0) for po in purchase_orders)
        
        if po_total == 0:
            score = 0.0
        else:
            diff_pct = abs(invoice_amount - po_total) / po_total * 100
            if diff_pct <= tolerance_pct:
                score = 1.0 - (diff_pct / tolerance_pct) * 0.1
            else:
                score = max(0.0, 1.0 - (diff_pct / 100))
        
        return {
            "score": score,
            "matched": score >= threshold,
            "invoice_amount": invoice_amount,
            "po_total": po_total,
        }
    
    def _save_checkpoint(self, params: dict[str, Any]) -> dict[str, Any]:
        """Save checkpoint (mock - actual save in DB)."""
        return {
            "saved": True,
            "checkpoint_id": params.get("checkpoint_id"),
            "db_tool": params.get("db_tool", "sqlite"),
        }
    
    def _build_accounting_entries(self, params: dict[str, Any]) -> dict[str, Any]:
        """Build accounting journal entries."""
        return {
            "entries_created": 2,
            "total_debit": params.get("amount", 0),
            "total_credit": params.get("amount", 0),
        }
    
    def _apply_approval_policy(self, params: dict[str, Any]) -> dict[str, Any]:
        """Apply approval policy."""
        amount = params.get("amount", 0)
        risk_score = params.get("risk_score", 0)
        
        auto_approve_threshold = 10000
        
        if amount <= auto_approve_threshold and risk_score < 0.5:
            return {"approved": True, "method": "auto", "approver": "SYSTEM"}
        else:
            return {"approved": False, "method": "escalated", "approver": "finance_manager"}
    
    def _output_final_payload(self, params: dict[str, Any]) -> dict[str, Any]:
        """Output final payload."""
        return {
            "output": True,
            "payload_size": len(str(params.get("payload", {}))),
            "audit_entries": len(params.get("audit_log", [])),
        }
