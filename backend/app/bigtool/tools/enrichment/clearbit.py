"""Clearbit Enrichment Tool (Mock Implementation)."""

from typing import Any
import random

from faker import Faker

from app.bigtool.base import BaseEnrichmentTool


fake = Faker()


class ClearbitEnrichment(BaseEnrichmentTool):
    """
    Clearbit company enrichment tool.
    
    Mock implementation that simulates Clearbit API responses.
    In production, this would use Clearbit SDK.
    """
    
    def __init__(self):
        super().__init__(
            name="clearbit",
            provider="Clearbit",
            description="B2B company data enrichment via Clearbit",
            is_mock=True,
        )
    
    def _execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Enrich company data using Clearbit (mock)."""
        company_name = params.get("vendor_name", params.get("company_name", ""))
        domain = params.get("domain", "")
        
        # Generate mock enrichment data
        return {
            "company": {
                "name": company_name,
                "legal_name": f"{company_name} Inc.",
                "domain": domain or f"{company_name.lower().replace(' ', '')}.com",
                "industry": fake.bs(),
                "sector": random.choice(["Technology", "Manufacturing", "Services", "Retail"]),
                "employee_count": random.randint(10, 5000),
                "revenue_range": random.choice(["$1M-$10M", "$10M-$50M", "$50M-$100M", "$100M+"]),
                "founded_year": random.randint(1990, 2020),
                "location": {
                    "city": fake.city(),
                    "state": fake.state(),
                    "country": "US",
                },
                "description": fake.paragraph(),
            },
            "metrics": {
                "alexa_rank": random.randint(1000, 1000000),
                "employees_range": f"{random.randint(10, 100)}-{random.randint(100, 1000)}",
            },
            "risk_indicators": {
                "credit_score": random.randint(600, 850),
                "risk_rating": random.choice(["LOW", "MEDIUM", "HIGH"]),
                "years_in_business": random.randint(1, 30),
            },
            "enriched": True,
            "provider": self.provider,
        }


__all__ = ["ClearbitEnrichment"]

