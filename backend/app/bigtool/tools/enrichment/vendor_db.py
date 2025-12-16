"""Vendor Database Enrichment Tool (Mock Implementation)."""

from typing import Any
import random

from faker import Faker

from app.bigtool.base import BaseEnrichmentTool


fake = Faker()


class VendorDBEnrichment(BaseEnrichmentTool):
    """
    Internal vendor database enrichment tool.
    
    Mock implementation that simulates internal vendor lookup.
    In production, this would query internal vendor database.
    """
    
    def __init__(self):
        super().__init__(
            name="vendor_db",
            provider="Internal",
            description="Internal vendor database lookup",
            is_mock=True,
        )
    
    def _execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Lookup vendor in internal database (mock)."""
        vendor_name = params.get("vendor_name", "")
        vendor_id = params.get("vendor_id", "")
        tax_id = params.get("tax_id", "")
        
        # Simulate internal vendor database lookup
        vendor_code = f"VND-{random.randint(10000, 99999)}"
        
        return {
            "vendor": {
                "vendor_code": vendor_code,
                "name": vendor_name,
                "normalized_name": vendor_name.strip().upper(),
                "tax_id": tax_id or fake.ssn(),
                "status": random.choice(["ACTIVE", "ACTIVE", "ACTIVE", "PENDING", "INACTIVE"]),
                "category": random.choice(["SUPPLIER", "CONTRACTOR", "SERVICE_PROVIDER"]),
                "payment_terms": random.choice(["NET30", "NET45", "NET60", "2/10NET30"]),
                "currency": random.choice(["USD", "USD", "EUR", "GBP"]),
            },
            "history": {
                "first_transaction_date": fake.date_between(start_date="-5y", end_date="-1y").isoformat(),
                "last_transaction_date": fake.date_between(start_date="-90d", end_date="today").isoformat(),
                "total_transactions": random.randint(10, 500),
                "total_amount": round(random.uniform(50000, 5000000), 2),
                "avg_invoice_amount": round(random.uniform(1000, 50000), 2),
            },
            "compliance": {
                "verified": True,
                "last_verified_date": fake.date_between(start_date="-1y", end_date="today").isoformat(),
                "tax_compliant": True,
                "w9_on_file": True,
            },
            "risk": {
                "score": round(random.uniform(0, 0.3), 2),
                "rating": "LOW",
                "payment_history": random.choice(["EXCELLENT", "GOOD", "FAIR"]),
            },
            "found_in_db": True,
            "enriched": True,
            "provider": self.provider,
        }


__all__ = ["VendorDBEnrichment"]

