"""ATLAS Server - External integrations."""

from typing import Any
from datetime import datetime
import random

from faker import Faker

from app.utils.logger import logger
from app.utils.helpers import generate_id


fake = Faker()


class AtlasServer:
    """
    ATLAS MCP Server - Handles external integrations.
    
    Abilities:
    - ocr_extract
    - enrich_vendor
    - fetch_po
    - fetch_grn
    - fetch_history
    - human_review_action
    - post_to_erp
    - schedule_payment
    - notify_vendor
    - notify_finance_team
    """
    
    def execute(self, ability: str, params: dict[str, Any]) -> dict[str, Any]:
        """Execute ATLAS server ability."""
        handlers = {
            "ocr_extract": self._ocr_extract,
            "enrich_vendor": self._enrich_vendor,
            "fetch_po": self._fetch_po,
            "fetch_grn": self._fetch_grn,
            "fetch_history": self._fetch_history,
            "human_review_action": self._human_review_action,
            "post_to_erp": self._post_to_erp,
            "schedule_payment": self._schedule_payment,
            "notify_vendor": self._notify_vendor,
            "notify_finance_team": self._notify_finance_team,
        }
        
        handler = handlers.get(ability)
        if not handler:
            logger.warning(f"Unknown ATLAS ability: {ability}")
            return {"error": f"Unknown ability: {ability}"}
        
        return handler(params)
    
    def _ocr_extract(self, params: dict[str, Any]) -> dict[str, Any]:
        """Extract text from invoice attachments (mock)."""
        provider = params.get("provider", "google_vision")
        attachments = params.get("attachments", [])
        
        # Mock OCR response
        extracted_text = f"""
        INVOICE
        Invoice Number: INV-{fake.random_number(digits=6)}
        Date: {fake.date()}
        Vendor: {fake.company()}
        Amount: ${fake.random_number(digits=5)}.00
        PO Reference: PO-2024-001
        """
        
        return {
            "extracted_text": extracted_text.strip(),
            "confidence": round(random.uniform(0.85, 0.99), 2),
            "provider": provider,
            "pages_processed": len(attachments) or 1,
        }
    
    def _enrich_vendor(self, params: dict[str, Any]) -> dict[str, Any]:
        """Enrich vendor data (mock)."""
        vendor_name = params.get("vendor_name", "")
        provider = params.get("provider", "clearbit")
        
        return {
            "vendor_name": vendor_name,
            "enriched": True,
            "provider": provider,
            "data": {
                "legal_name": vendor_name,
                "address": fake.address(),
                "phone": fake.phone_number(),
                "email": fake.company_email(),
                "industry": fake.bs(),
                "employee_count": random.randint(10, 1000),
                "credit_score": random.randint(600, 850),
                "risk_rating": random.choice(["LOW", "MEDIUM", "HIGH"]),
            },
        }
    
    def _fetch_po(self, params: dict[str, Any]) -> dict[str, Any]:
        """Fetch purchase orders from ERP (mock)."""
        vendor_name = params.get("vendor_name", "")
        po_numbers = params.get("po_numbers", [])
        connector = params.get("connector", "mock_erp")
        
        # Generate mock POs
        purchase_orders = []
        for i, po_num in enumerate(po_numbers or ["PO-2024-001"]):
            purchase_orders.append({
                "po_id": po_num,
                "vendor": vendor_name,
                "amount": random.randint(5000, 20000),
                "currency": "USD",
                "status": "APPROVED",
                "created_date": fake.date_between(start_date="-90d", end_date="-30d").isoformat(),
            })
        
        return {
            "purchase_orders": purchase_orders,
            "total_count": len(purchase_orders),
            "connector": connector,
        }
    
    def _fetch_grn(self, params: dict[str, Any]) -> dict[str, Any]:
        """Fetch goods received notes (mock)."""
        po_ids = params.get("po_ids", [])
        connector = params.get("connector", "mock_erp")
        
        grns = []
        for po_id in po_ids:
            grns.append({
                "grn_id": f"GRN-{generate_id('')[:8]}",
                "po_id": po_id,
                "received_date": fake.date_between(start_date="-30d", end_date="today").isoformat(),
                "status": "RECEIVED",
                "quantity_received": random.randint(1, 100),
            })
        
        return {
            "grns": grns,
            "total_count": len(grns),
            "connector": connector,
        }
    
    def _fetch_history(self, params: dict[str, Any]) -> dict[str, Any]:
        """Fetch historical invoices (mock)."""
        vendor_name = params.get("vendor_name", "")
        connector = params.get("connector", "mock_erp")
        
        invoices = []
        for i in range(random.randint(1, 5)):
            invoices.append({
                "invoice_id": f"HIST-INV-{generate_id('')[:6]}",
                "vendor": vendor_name,
                "amount": random.randint(1000, 50000),
                "date": fake.date_between(start_date="-1y", end_date="-30d").isoformat(),
                "status": "PAID",
            })
        
        return {
            "invoices": invoices,
            "total_count": len(invoices),
            "connector": connector,
        }
    
    def _human_review_action(self, params: dict[str, Any]) -> dict[str, Any]:
        """Process human review action."""
        return {
            "processed": True,
            "checkpoint_id": params.get("checkpoint_id"),
            "decision": params.get("decision"),
            "reviewer_id": params.get("reviewer_id"),
            "processed_at": datetime.utcnow().isoformat(),
        }
    
    def _post_to_erp(self, params: dict[str, Any]) -> dict[str, Any]:
        """Post journal entries to ERP (mock)."""
        connector = params.get("connector", "mock_erp")
        
        return {
            "posted": True,
            "transaction_id": f"ERP-TXN-{generate_id('')[:8]}",
            "entries_posted": len(params.get("entries", [])),
            "connector": connector,
            "posted_at": datetime.utcnow().isoformat(),
        }
    
    def _schedule_payment(self, params: dict[str, Any]) -> dict[str, Any]:
        """Schedule payment (mock)."""
        return {
            "scheduled": True,
            "payment_id": f"PAY-{generate_id('')[:8]}",
            "amount": params.get("amount", 0),
            "due_date": params.get("due_date"),
            "vendor": params.get("vendor"),
            "scheduled_at": datetime.utcnow().isoformat(),
        }
    
    def _notify_vendor(self, params: dict[str, Any]) -> dict[str, Any]:
        """Send notification to vendor (mock)."""
        provider = params.get("provider", "sendgrid")
        
        return {
            "sent": True,
            "recipient": params.get("vendor_name"),
            "subject": f"Invoice {params.get('invoice_id')} Processed",
            "provider": provider,
            "sent_at": datetime.utcnow().isoformat(),
        }
    
    def _notify_finance_team(self, params: dict[str, Any]) -> dict[str, Any]:
        """Send notification to finance team (mock)."""
        provider = params.get("provider", "sendgrid")
        
        return {
            "sent": True,
            "recipient": "finance-team@company.com",
            "subject": f"Invoice {params.get('invoice_id')} - {params.get('approval_status')}",
            "provider": provider,
            "sent_at": datetime.utcnow().isoformat(),
        }
