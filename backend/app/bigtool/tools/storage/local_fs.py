"""Local File System Storage Tool."""

from typing import Any
from pathlib import Path
import random
from datetime import datetime

from faker import Faker

from app.bigtool.base import BaseStorageTool


fake = Faker()


class LocalFSStorage(BaseStorageTool):
    """
    Local file system storage tool.
    
    Uses local filesystem for development and testing.
    """
    
    def __init__(self, base_path: str = "./data/storage"):
        super().__init__(
            name="local_fs",
            provider="Local",
            description="Local file system storage for dev/testing",
            is_mock=True,
            config={"base_path": base_path},
        )
        self.base_path = Path(base_path)
    
    def _execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Execute local storage operation."""
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
        """Upload file to local filesystem (mock)."""
        filename = params.get("filename", f"{fake.uuid4()}.pdf")
        directory = params.get("directory", "invoices")
        
        # In a real implementation, this would save the file
        file_path = self.base_path / directory / filename
        
        return {
            "uploaded": True,
            "path": str(file_path),
            "filename": filename,
            "size_bytes": random.randint(10000, 5000000),
            "created_at": datetime.utcnow().isoformat(),
            "provider": self.provider,
        }
    
    def _download(self, params: dict[str, Any]) -> dict[str, Any]:
        """Download file from local filesystem (mock)."""
        file_path = params.get("path", "")
        
        return {
            "downloaded": True,
            "path": file_path,
            "size_bytes": random.randint(10000, 5000000),
            "content_type": "application/pdf",
            "provider": self.provider,
        }
    
    def _list(self, params: dict[str, Any]) -> dict[str, Any]:
        """List files in local directory (mock)."""
        directory = params.get("directory", "invoices")
        dir_path = self.base_path / directory
        
        # Mock file list
        files = [
            {
                "name": f"{fake.uuid4()[:8]}.pdf",
                "size": random.randint(10000, 5000000),
                "modified": fake.date_time_this_month().isoformat(),
            }
            for _ in range(random.randint(1, 10))
        ]
        
        return {
            "directory": str(dir_path),
            "files": files,
            "count": len(files),
            "provider": self.provider,
        }
    
    def _delete(self, params: dict[str, Any]) -> dict[str, Any]:
        """Delete file from local filesystem (mock)."""
        file_path = params.get("path", "")
        
        return {
            "deleted": True,
            "path": file_path,
            "provider": self.provider,
        }


__all__ = ["LocalFSStorage"]

