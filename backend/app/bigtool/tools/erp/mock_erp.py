"""Mock ERP Connector for demo/testing."""

from typing import Any
import random

from faker import Faker

from app.bigtool.base import BaseERPConnector


fake = Faker()


class MockERPConnector(BaseERPConnector):
    """
    Mock ERP connector for demo and testing.
    
    Provides realistic mock data without external dependencies.
    """
    
    def __init__(self):
        super().__init__(
            name="mock_erp",
            provider="Mock",
            description="Mock ERP connector for demo/testing",
            is_mock=True,
        )
    
    def _execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute mock ERP operation."""
        operation = params.get("operation", "query")
        
        if operation == "fetch_po":
            return self._fetch_purchase_orders(params)
        elif operation == "fetch_grn":
            return self._fetch_grns(params)
        elif operation == "post_invoice":
            return self._post_invoice(params)
        elif operation == "fetch_history":
            return self._fetch_history(params)
        elif operation == "schedule_payment":
            return self._schedule_payment(params)
        else:
            return {"operation": operation, "status": "completed", "provider": self.provider}
    
    def _fetch_purchase_orders(self, params: dict[str, Any]) -> dict[str, Any]:
        """Fetch mock purchase orders."""
        vendor = params.get("vendor_name", "")
        invoice_amount = params.get("invoice_amount", 0)
        po_numbers = params.get("po_numbers", [])
        
        purchase_orders = []
        
        # If invoice amount provided, create matching PO for demo
        if invoice_amount > 0 and not po_numbers:
            po_numbers = [f"PO-2024-{random.randint(1000, 9999)}"]
        
        for i, po_num in enumerate(po_numbers or [f"PO-2024-{random.randint(1000, 9999)}"]):
            # For demo, make first PO match invoice amount closely
            if i == 0 and invoice_amount > 0:
                amount = invoice_amount * random.uniform(0.98, 1.02)  # Within 2% tolerance
            else:
                amount = round(random.uniform(5000, 20000), 2)
            
            purchase_orders.append({
                "po_id": po_num,
                "vendor": vendor,
                "amount": round(amount, 2),
                "currency": "USD",
                "status": "APPROVED",
                "created_date": fake.date_between(start_date="-90d", end_date="-30d").isoformat(),
                "line_items": [
                    {
                        "description": fake.bs(),
                        "quantity": random.randint(1, 10),
                        "unit_price": round(random.uniform(100, 2000), 2),
                    }
                    for _ in range(random.randint(1, 3))
                ],
            })
        
        return {
            "purchase_orders": purchase_orders,
            "total_count": len(purchase_orders),
            "provider": self.provider,
        }
    
    def _fetch_grns(self, params: dict[str, Any]) -> dict[str, Any]:
        """Fetch mock goods receipt notes."""
        po_ids = params.get("po_ids", [])
        
        grns = []
        for po_id in po_ids or [f"PO-2024-{random.randint(1000, 9999)}"]:
            grns.append({
                "grn_id": f"GRN-{fake.uuid4()[:8].upper()}",
                "po_id": po_id,
                "received_date": fake.date_between(start_date="-30d", end_date="today").isoformat(),
                "status": "RECEIVED",
                "quantity_received": random.randint(1, 100),
                "received_by": fake.name(),
            })
        
        return {
            "grns": grns,
            "total_count": len(grns),
            "provider": self.provider,
        }
    
    def _post_invoice(self, params: dict[str, Any]) -> dict[str, Any]:
        """Post invoice to mock ERP."""
        return {
            "posted": True,
            "erp_txn_id": f"TXN-{fake.uuid4()[:8].upper()}",
            "journal_id": f"JE-{random.randint(100000, 999999)}",
            "posting_date": fake.date_this_month().isoformat(),
            "entries_created": params.get("entries_count", 2),
            "provider": self.provider,
        }
    
    def _fetch_history(self, params: dict[str, Any]) -> dict[str, Any]:
        """Fetch mock invoice history."""
        vendor = params.get("vendor_name", "")
        
        invoices = []
        for i in range(random.randint(2, 6)):
            invoices.append({
                "invoice_id": f"HIST-INV-{fake.uuid4()[:6].upper()}",
                "vendor": vendor,
                "amount": round(random.uniform(1000, 50000), 2),
                "date": fake.date_between(start_date="-1y", end_date="-30d").isoformat(),
                "status": "PAID",
                "payment_date": fake.date_between(start_date="-11m", end_date="-1d").isoformat(),
            })
        
        return {
            "invoices": invoices,
            "total_count": len(invoices),
            "provider": self.provider,
        }
    
    def _schedule_payment(self, params: dict[str, Any]) -> dict[str, Any]:
        """Schedule payment in mock ERP."""
        return {
            "scheduled": True,
            "payment_id": f"PAY-{fake.uuid4()[:8].upper()}",
            "amount": params.get("amount", 0),
            "currency": params.get("currency", "USD"),
            "scheduled_date": params.get("due_date", fake.date_between(start_date="today", end_date="+30d").isoformat()),
            "payment_method": random.choice(["ACH", "WIRE", "CHECK"]),
            "provider": self.provider,
        }


__all__ = ["MockERPConnector"]

