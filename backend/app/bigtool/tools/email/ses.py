"""AWS SES Email Tool (Mock Implementation)."""

from typing import Any
from datetime import datetime

from faker import Faker

from app.bigtool.base import BaseEmailTool


fake = Faker()


class SESEmail(BaseEmailTool):
    """
    AWS SES email tool.
    
    Mock implementation that simulates SES API responses.
    In production, this would use boto3 SES client.
    """
    
    def __init__(self):
        super().__init__(
            name="ses",
            provider="AWS",
            description="AWS Simple Email Service",
            is_mock=True,
        )
    
    def _execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Send email via AWS SES (mock)."""
        to_email = params.get("to", params.get("recipient", ""))
        from_email = params.get("from", "noreply@invoice-agent.com")
        subject = params.get("subject", "Invoice Notification")
        
        return {
            "sent": True,
            "message_id": f"ses-{fake.uuid4()}",
            "to": to_email,
            "from": from_email,
            "subject": subject,
            "request_id": fake.uuid4()[:8],
            "sent_at": datetime.utcnow().isoformat(),
            "provider": self.provider,
        }


__all__ = ["SESEmail"]

