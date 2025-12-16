"""AWS Textract OCR Tool (Mock Implementation)."""

from typing import Any
import random

from faker import Faker

from app.bigtool.base import BaseOCRTool


fake = Faker()


class AWSTextractOCR(BaseOCRTool):
    """
    AWS Textract OCR tool.
    
    Mock implementation that simulates AWS Textract responses.
    In production, this would use boto3 textract client.
    """
    
    def __init__(self):
        super().__init__(
            name="aws_textract",
            provider="AWS",
            description="AWS Textract with table/form extraction",
            is_mock=True,
        )
    
    def _execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Extract text from document using AWS Textract (mock)."""
        attachments = params.get("attachments", [])
        
        # Generate mock OCR response with table structure
        invoice_number = f"INV-{fake.random_number(digits=6)}"
        vendor_name = fake.company()
        amount = round(random.uniform(1000, 50000), 2)
        
        extracted_text = f"""
INVOICE

Invoice Number: {invoice_number}
Date: {fake.date_this_year().isoformat()}
Due Date: {fake.date_between(start_date='today', end_date='+30d').isoformat()}

Vendor: {vendor_name}
Tax ID: {fake.ssn()}

Total: ${amount:.2f}

PO Reference: PO-2024-{random.randint(1000, 9999)}
        """.strip()
        
        # Textract returns structured table data
        tables = [
            {
                "table_id": "table_1",
                "rows": [
                    ["Description", "Qty", "Unit Price", "Total"],
                    [fake.bs(), str(random.randint(1, 10)), f"${random.randint(100, 1000)}", f"${random.randint(1000, 5000)}"],
                    [fake.bs(), str(random.randint(1, 5)), f"${random.randint(200, 2000)}", f"${random.randint(2000, 10000)}"],
                ],
            }
        ]
        
        # Textract returns form key-value pairs
        forms = {
            "Invoice Number": invoice_number,
            "Date": fake.date_this_year().isoformat(),
            "Vendor": vendor_name,
            "Total": f"${amount:.2f}",
        }
        
        return {
            "extracted_text": extracted_text,
            "confidence": round(random.uniform(0.90, 0.98), 3),
            "language": "en",
            "pages_processed": len(attachments) if attachments else 1,
            "tables": tables,
            "forms": forms,
            "provider": self.provider,
            "job_id": f"textract-{fake.uuid4()[:8]}",
        }


__all__ = ["AWSTextractOCR"]

