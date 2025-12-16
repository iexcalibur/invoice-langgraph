"""Google Cloud Storage Tool (Mock Implementation)."""

from typing import Any
import random

from faker import Faker

from app.bigtool.base import BaseStorageTool


fake = Faker()


class GCSStorage(BaseStorageTool):
    """
    Google Cloud Storage tool.
    
    Mock implementation that simulates GCS API responses.
    In production, this would use google-cloud-storage SDK.
    """
    
    def __init__(self):
        super().__init__(
            name="gcs",
            provider="Google Cloud",
            description="Google Cloud Storage",
            is_mock=True,
        )
    
    def _execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute GCS storage operation (mock)."""
        operation = params.get("operation", "upload")
        
        if operation == "upload":
            return self._upload(params)
        elif operation == "download":
            return self._download(params)
        elif operation == "list":
            return self._list(params)
        elif operation == "delete":
            return self._delete(params)
        else:
            return {"operation": operation, "status": "completed", "provider": self.provider}
    
    def _upload(self, params: dict[str, Any]) -> dict[str, Any]:
        """Upload file to GCS (mock)."""
        bucket = params.get("bucket", "invoice-bucket")
        blob_name = params.get("blob_name", f"invoices/{fake.uuid4()}.pdf")
        
        return {
            "uploaded": True,
            "bucket": bucket,
            "blob_name": blob_name,
            "generation": random.randint(1000000, 9999999),
            "md5_hash": fake.md5()[:24],
            "size_bytes": random.randint(10000, 5000000),
            "url": f"gs://{bucket}/{blob_name}",
            "provider": self.provider,
        }
    
    def _download(self, params: dict[str, Any]) -> dict[str, Any]:
        """Download file from GCS (mock)."""
        return {
            "downloaded": True,
            "bucket": params.get("bucket", "invoice-bucket"),
            "blob_name": params.get("blob_name", ""),
            "size_bytes": random.randint(10000, 5000000),
            "content_type": "application/pdf",
            "provider": self.provider,
        }
    
    def _list(self, params: dict[str, Any]) -> dict[str, Any]:
        """List blobs in GCS bucket (mock)."""
        bucket = params.get("bucket", "invoice-bucket")
        prefix = params.get("prefix", "invoices/")
        
        blobs = [
            {
                "name": f"{prefix}{fake.uuid4()[:8]}.pdf",
                "size": random.randint(10000, 5000000),
                "updated": fake.date_time_this_month().isoformat(),
            }
            for _ in range(random.randint(1, 10))
        ]
        
        return {
            "bucket": bucket,
            "prefix": prefix,
            "blobs": blobs,
            "count": len(blobs),
            "provider": self.provider,
        }
    
    def _delete(self, params: dict[str, Any]) -> dict[str, Any]:
        """Delete blob from GCS (mock)."""
        return {
            "deleted": True,
            "bucket": params.get("bucket", "invoice-bucket"),
            "blob_name": params.get("blob_name", ""),
            "provider": self.provider,
        }


__all__ = ["GCSStorage"]

