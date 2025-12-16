"""Helper utilities for Invoice LangGraph Agent."""

import uuid
from datetime import datetime, timezone
from typing import Any


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID with optional prefix."""
    unique_id = uuid.uuid4().hex[:16]
    return f"{prefix}_{unique_id}" if prefix else unique_id


def generate_workflow_id(invoice_id: str | None = None) -> str:
    """Generate a workflow ID."""
    if invoice_id:
        return f"wf_{invoice_id}_{uuid.uuid4().hex[:8]}"
    return generate_id("wf")


def generate_checkpoint_id(workflow_id: str) -> str:
    """Generate a checkpoint ID."""
    return f"cp_{workflow_id}_{uuid.uuid4().hex[:8]}"


def generate_review_url(checkpoint_id: str, base_url: str = "http://localhost:3000") -> str:
    """Generate human review URL."""
    return f"{base_url}/review/{checkpoint_id}"


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    """Get current UTC datetime as ISO string."""
    return utc_now().isoformat()


def format_duration(seconds: float) -> str:
    """Format duration in human-readable form."""
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    else:
        return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m"


def safe_get(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Safely get nested dictionary value."""
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
        else:
            return default
        if result is None:
            return default
    return result


def calculate_match_score(invoice_amount: float, po_amount: float, tolerance_pct: float = 5.0) -> float:
    """Calculate match score between invoice and PO amounts."""
    if po_amount == 0:
        return 0.0 if invoice_amount != 0 else 1.0
    
    diff_pct = abs(invoice_amount - po_amount) / po_amount * 100
    
    if diff_pct <= tolerance_pct:
        return 1.0 - (diff_pct / tolerance_pct) * 0.1
    else:
        return max(0.0, 1.0 - (diff_pct / 100))


__all__ = [
    "generate_id", "generate_workflow_id", "generate_checkpoint_id", "generate_review_url",
    "utc_now", "utc_now_iso", "format_duration", "safe_get", "calculate_match_score",
]
