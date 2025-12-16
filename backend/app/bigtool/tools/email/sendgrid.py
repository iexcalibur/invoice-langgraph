"""SendGrid Email Tool (Mock Implementation)."""

from typing import Any
from datetime import datetime

from faker import Faker

from app.bigtool.base import BaseEmailTool


fake = Faker()


class SendGridEmail(BaseEmailTool):
    """
    SendGrid email tool.
    
    Mock implementation that simulates SendGrid API responses.
    In production, this would use sendgrid SDK.
    """
    
    def __init__(self):
        super().__init__(
            name="sendgrid",
            provider="SendGrid",
            description="SendGrid transactional email service",
            is_mock=True,
        )
    
    def _execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Send email via SendGrid (mock)."""
        to_email = params.get("to", params.get("recipient", ""))
        from_email = params.get("from", "noreply@invoice-agent.com")
        subject = params.get("subject", "Invoice Notification")
        
        return {
            "sent": True,
            "message_id": f"sg-{fake.uuid4()[:12]}",
            "to": to_email,
            "from": from_email,
            "subject": subject,
            "status": "queued",
            "sent_at": datetime.utcnow().isoformat(),
            "provider": self.provider,
        }


__all__ = ["SendGridEmail"]

