"""People Data Labs Enrichment Tool (Mock Implementation)."""

from typing import Any
import random

from faker import Faker

from app.bigtool.base import BaseEnrichmentTool


fake = Faker()


class PeopleDataLabsEnrichment(BaseEnrichmentTool):
    """
    People Data Labs enrichment tool.
    
    Mock implementation that simulates PDL API responses.
    In production, this would use PDL SDK.
    """
    
    def __init__(self):
        super().__init__(
            name="people_data_labs",
            provider="People Data Labs",
            description="Contact and person data enrichment",
            is_mock=True,
        )
    
    def _execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Enrich person/contact data using PDL (mock)."""
        email = params.get("email", "")
        name = params.get("name", "")
        company = params.get("company", params.get("vendor_name", ""))
        
        # Generate mock person enrichment data
        first_name = fake.first_name()
        last_name = fake.last_name()
        
        return {
            "person": {
                "full_name": name or f"{first_name} {last_name}",
                "first_name": first_name,
                "last_name": last_name,
                "email": email or fake.company_email(),
                "phone": fake.phone_number(),
                "linkedin_url": f"https://linkedin.com/in/{first_name.lower()}-{last_name.lower()}",
                "job_title": fake.job(),
                "seniority": random.choice(["entry", "senior", "manager", "director", "executive"]),
            },
            "company": {
                "name": company,
                "industry": fake.bs(),
                "size": random.choice(["1-10", "11-50", "51-200", "201-500", "500+"]),
            },
            "location": {
                "city": fake.city(),
                "state": fake.state(),
                "country": "US",
            },
            "enriched": True,
            "provider": self.provider,
            "confidence_score": round(random.uniform(0.7, 0.95), 2),
        }


__all__ = ["PeopleDataLabsEnrichment"]

