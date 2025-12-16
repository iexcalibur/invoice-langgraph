"""SAP ERP Connector (Mock Implementation)."""

from typing import Any
import random

from faker import Faker

from app.bigtool.base import BaseERPConnector


fake = Faker()


class SAPConnector(BaseERPConnector):
    """
    SAP S/4HANA ERP connector.
    
    Mock implementation that simulates SAP API responses.
    In production, this would use pyrfc or SAP REST APIs.
    """
    
    def __init__(self):
        super().__init__(
            name="sap_sandbox",
            provider="SAP",
            description="SAP S/4HANA sandbox connector",
            is_mock=True,
        )
    
    def _execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute SAP operation (mock)."""
        operation = params.get("operation", "query")
        
        if operation == "fetch_po":
            return self._fetch_purchase_orders(params)
        elif operation == "fetch_grn":
            return self._fetch_grns(params)
        elif operation == "post_invoice":
            return self._post_invoice(params)
        elif operation == "fetch_history":
            return self._fetch_history(params)
        else:
            return {"operation": operation, "status": "completed", "provider": self.provider}
    
    def _fetch_purchase_orders(self, params: dict[str, Any]) -> dict[str, Any]:
        """Fetch purchase orders from SAP."""
        vendor = params.get("vendor_name", "")
        po_numbers = params.get("po_numbers", [])
        
        purchase_orders = []
        for i, po_num in enumerate(po_numbers or [f"SAP-PO-{random.randint(1000, 9999)}"]):
            purchase_orders.append({
                "po_id": po_num,
                "sap_doc_number": f"45000{random.randint(10000, 99999)}",
                "vendor": vendor,
                "amount": round(random.uniform(5000, 50000), 2),
                "currency": "USD",
                "status": random.choice(["APPROVED", "OPEN", "CLOSED"]),
                "created_date": fake.date_between(start_date="-90d", end_date="-30d").isoformat(),
                "company_code": "1000",
                "plant": "1000",
            })
        
        return {
            "purchase_orders": purchase_orders,
            "total_count": len(purchase_orders),
            "provider": self.provider,
            "sap_system": "S4H",
        }
    
    def _fetch_grns(self, params: dict[str, Any]) -> dict[str, Any]:
        """Fetch goods receipt notes from SAP."""
        po_ids = params.get("po_ids", [])
        
        grns = []
        for po_id in po_ids or [f"SAP-PO-{random.randint(1000, 9999)}"]:
            grns.append({
                "grn_id": f"GRN-{random.randint(100000, 999999)}",
                "sap_doc_number": f"50000{random.randint(10000, 99999)}",
                "po_id": po_id,
                "received_date": fake.date_between(start_date="-30d", end_date="today").isoformat(),
                "status": "RECEIVED",
                "quantity_received": random.randint(1, 100),
                "movement_type": "101",
            })
        
        return {
            "grns": grns,
            "total_count": len(grns),
            "provider": self.provider,
        }
    
    def _post_invoice(self, params: dict[str, Any]) -> dict[str, Any]:
        """Post invoice to SAP."""
        return {
            "posted": True,
            "sap_document_number": f"51000{random.randint(10000, 99999)}",
            "fiscal_year": "2024",
            "posting_date": fake.date_this_month().isoformat(),
            "provider": self.provider,
        }
    
    def _fetch_history(self, params: dict[str, Any]) -> dict[str, Any]:
        """Fetch invoice history from SAP."""
        vendor = params.get("vendor_name", "")
        
        invoices = []
        for i in range(random.randint(2, 8)):
            invoices.append({
                "invoice_id": f"SAP-INV-{random.randint(100000, 999999)}",
                "vendor": vendor,
                "amount": round(random.uniform(1000, 50000), 2),
                "date": fake.date_between(start_date="-1y", end_date="-30d").isoformat(),
                "status": "PAID",
            })
        
        return {
            "invoices": invoices,
            "total_count": len(invoices),
            "provider": self.provider,
        }


__all__ = ["SAPConnector"]

