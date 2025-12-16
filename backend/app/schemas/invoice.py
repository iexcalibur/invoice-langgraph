"""Invoice-related Pydantic schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class LineItem(BaseModel):
    """Line item in an invoice."""
    
    desc: str = Field(..., description="Item description")
    qty: float = Field(..., description="Quantity")
    unit_price: float = Field(..., description="Unit price")
    total: float = Field(..., description="Line total")


class InvoicePayload(BaseModel):
    """Invoice payload for workflow invocation."""
    
    invoice_id: str = Field(..., description="Unique invoice identifier")
    vendor_name: str = Field(..., description="Vendor/supplier name")
    vendor_tax_id: str | None = Field(None, description="Vendor tax ID (PAN/GST/TIN)")
    invoice_date: str | None = Field(None, description="Invoice date")
    due_date: str | None = Field(None, description="Payment due date")
    amount: float = Field(..., description="Total invoice amount")
    currency: str = Field("USD", description="Currency code")
    line_items: list[LineItem] = Field(default_factory=list, description="Invoice line items")
    attachments: list[str] = Field(default_factory=list, description="Attachment URLs/paths")
    
    model_config = {"json_schema_extra": {
        "example": {
            "invoice_id": "INV-2024-001",
            "vendor_name": "Acme Corporation",
            "vendor_tax_id": "GSTIN123456",
            "invoice_date": "2024-01-15",
            "due_date": "2024-02-15",
            "amount": 15000.00,
            "currency": "USD",
            "line_items": [
                {"desc": "Consulting Services", "qty": 10, "unit_price": 1500.00, "total": 15000.00}
            ],
            "attachments": ["invoice_scan.pdf"]
        }
    }}


class InvokeResponse(BaseModel):
    """Response from workflow invocation."""
    
    success: bool = Field(True, description="Whether invocation was successful")
    workflow_id: str = Field(..., description="Generated workflow ID")
    invoice_id: str = Field(..., description="Invoice ID being processed")
    status: str = Field(..., description="Initial workflow status")
    current_stage: str | None = Field(None, description="Current stage (if started)")
    message: str = Field("Workflow started", description="Status message")
    timestamp: str = Field(..., description="Invocation timestamp")
    
    model_config = {"json_schema_extra": {
        "example": {
            "success": True,
            "workflow_id": "wf_INV-2024-001_abc123",
            "invoice_id": "INV-2024-001",
            "status": "RUNNING",
            "current_stage": "INTAKE",
            "message": "Workflow started successfully",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    }}
