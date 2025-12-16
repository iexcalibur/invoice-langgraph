"""Google Vision OCR Tool (Mock Implementation)."""

from typing import Any
import random

from faker import Faker

from app.bigtool.base import BaseOCRTool


fake = Faker()


class GoogleVisionOCR(BaseOCRTool):
    """
    Google Cloud Vision OCR tool.
    
    Mock implementation that simulates Google Vision API responses.
    In production, this would use google-cloud-vision SDK.
    """
    
    def __init__(self):
        super().__init__(
            name="google_vision",
            provider="Google Cloud",
            description="Google Cloud Vision OCR with high accuracy for invoices",
            is_mock=True,
        )
    
    def _execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Extract text from document using Google Vision (mock)."""
        attachments = params.get("attachments", [])
        document_type = params.get("document_type", "invoice")
        
        # Generate mock OCR response
        invoice_number = f"INV-{fake.random_number(digits=6)}"
        vendor_name = fake.company()
        amount = round(random.uniform(1000, 50000), 2)
        
        extracted_text = f"""
INVOICE

Invoice Number: {invoice_number}
Date: {fake.date_this_year().isoformat()}
Due Date: {fake.date_between(start_date='today', end_date='+30d').isoformat()}

Vendor: {vendor_name}
Address: {fake.address()}
Tax ID: {fake.ssn()}

Bill To:
{fake.company()}
{fake.address()}

Items:
1. {fake.bs()} - Qty: {random.randint(1, 10)} x ${random.randint(100, 1000)}.00
2. {fake.bs()} - Qty: {random.randint(1, 5)} x ${random.randint(200, 2000)}.00

Subtotal: ${amount:.2f}
Tax (10%): ${amount * 0.1:.2f}
Total: ${amount * 1.1:.2f}

PO Reference: PO-2024-{random.randint(1000, 9999)}

Payment Terms: Net 30
        """.strip()
        
        return {
            "extracted_text": extracted_text,
            "confidence": round(random.uniform(0.92, 0.99), 3),
            "language": "en",
            "pages_processed": len(attachments) if attachments else 1,
            "document_type_detected": document_type,
            "bounding_boxes": [],  # Would contain text positions in real implementation
            "provider": self.provider,
        }


__all__ = ["GoogleVisionOCR"]

