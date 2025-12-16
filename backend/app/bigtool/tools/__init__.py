"""
Bigtool Tool Implementations.

All tool implementations organized by capability:
- ocr/: OCR tools (Google Vision, Tesseract, AWS Textract)
- enrichment/: Enrichment tools (Clearbit, People Data Labs, Vendor DB)
- erp/: ERP connectors (SAP, NetSuite, Mock)
- storage/: Storage tools (S3, GCS, Local FS)
- email/: Email tools (SendGrid, SES, SMTP)
- db/: Database tools (Postgres, SQLite, DynamoDB)
"""

from app.bigtool.tools.ocr import (
    GoogleVisionOCR,
    TesseractOCR,
    AWSTextractOCR,
)
from app.bigtool.tools.enrichment import (
    ClearbitEnrichment,
    PeopleDataLabsEnrichment,
    VendorDBEnrichment,
)
from app.bigtool.tools.erp import (
    SAPConnector,
    NetSuiteConnector,
    MockERPConnector,
)
from app.bigtool.tools.storage import (
    S3Storage,
    GCSStorage,
    LocalFSStorage,
)
from app.bigtool.tools.email import (
    SendGridEmail,
    SESEmail,
    SMTPEmail,
)
from app.bigtool.tools.db import (
    PostgresTool,
    SQLiteTool,
    DynamoDBTool,
)


__all__ = [
    # OCR
    "GoogleVisionOCR",
    "TesseractOCR",
    "AWSTextractOCR",
    # Enrichment
    "ClearbitEnrichment",
    "PeopleDataLabsEnrichment",
    "VendorDBEnrichment",
    # ERP
    "SAPConnector",
    "NetSuiteConnector",
    "MockERPConnector",
    # Storage
    "S3Storage",
    "GCSStorage",
    "LocalFSStorage",
    # Email
    "SendGridEmail",
    "SESEmail",
    "SMTPEmail",
    # DB
    "PostgresTool",
    "SQLiteTool",
    "DynamoDBTool",
]

