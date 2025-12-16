"""Tesseract OCR Tool (Mock Implementation)."""

from typing import Any
import random

from faker import Faker

from app.bigtool.base import BaseOCRTool


fake = Faker()


class TesseractOCR(BaseOCRTool):
    """
    Tesseract OCR tool.
    
    Mock implementation that simulates Tesseract responses.
    In production, this would use pytesseract.
    """
    
    def __init__(self):
        super().__init__(
            name="tesseract",
            provider="Tesseract OSS",
            description="Open-source Tesseract OCR engine",
            is_mock=True,
        )
    
    def _execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Extract text from document using Tesseract (mock)."""
        attachments = params.get("attachments", [])
        
        # Generate mock OCR response (slightly lower quality than Google)
        invoice_number = f"INV-{fake.random_number(digits=6)}"
        vendor_name = fake.company()
        amount = round(random.uniform(1000, 50000), 2)
        
        extracted_text = f"""
INVOICE

Invoice Number: {invoice_number}
Date: {fake.date_this_year().isoformat()}

Vendor: {vendor_name}
{fake.address()}

Total Amount: ${amount:.2f}

PO Reference: PO-2024-{random.randint(1000, 9999)}
        """.strip()
        
        return {
            "extracted_text": extracted_text,
            "confidence": round(random.uniform(0.80, 0.92), 3),
            "language": "en",
            "pages_processed": len(attachments) if attachments else 1,
            "provider": self.provider,
            "engine_version": "5.3.0",
        }


__all__ = ["TesseractOCR"]

