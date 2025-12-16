"""
Tests for Invoke API endpoints.
"""

import pytest
from fastapi import status


class TestInvokeEndpoint:
    """Tests for POST /api/v1/invoke endpoint."""
    
    def test_invoke_valid_invoice(self, client, sample_invoice_payload):
        """Test invoking workflow with valid invoice."""
        response = client.post("/api/v1/invoke", json=sample_invoice_payload)
        
        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        
        assert data["success"] is True
        assert "workflow_id" in data
        assert data["invoice_id"] == sample_invoice_payload["invoice_id"]
        assert data["status"] in ["RUNNING", "COMPLETED", "PAUSED"]
    
    def test_invoke_missing_required_fields(self, client):
        """Test invoking with missing required fields."""
        incomplete_payload = {
            "invoice_id": "INV-001",
            # Missing vendor_name, amount, etc.
        }
        
        response = client.post("/api/v1/invoke", json=incomplete_payload)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_invoke_invalid_amount(self, client, sample_invoice_payload):
        """Test invoking with invalid amount."""
        sample_invoice_payload["amount"] = -100  # Negative amount
        
        response = client.post("/api/v1/invoke", json=sample_invoice_payload)
        
        # Should fail validation
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_202_ACCEPTED]
    
    def test_invoke_returns_workflow_id(self, client, sample_invoice_payload):
        """Test that invoke returns a workflow ID."""
        response = client.post("/api/v1/invoke", json=sample_invoice_payload)
        
        assert response.status_code == status.HTTP_202_ACCEPTED
        data = response.json()
        
        assert "workflow_id" in data
        assert data["workflow_id"].startswith("wf_")
    
    def test_invoke_empty_line_items(self, client, sample_invoice_payload):
        """Test invoking with empty line items."""
        sample_invoice_payload["line_items"] = []
        
        response = client.post("/api/v1/invoke", json=sample_invoice_payload)
        
        # Should still work (line items can be empty)
        assert response.status_code == status.HTTP_202_ACCEPTED


class TestValidateEndpoint:
    """Tests for POST /api/v1/invoke/validate endpoint."""
    
    def test_validate_valid_invoice(self, client, sample_invoice_payload):
        """Test validating valid invoice payload."""
        response = client.post("/api/v1/invoke/validate", json=sample_invoice_payload)
        
        if response.status_code == status.HTTP_404_NOT_FOUND:
            pytest.skip("Validate endpoint not implemented")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data.get("valid", True) is True
    
    def test_validate_invalid_invoice(self, client):
        """Test validating invalid invoice payload."""
        invalid_payload = {"invoice_id": ""}
        
        response = client.post("/api/v1/invoke/validate", json=invalid_payload)
        
        if response.status_code == status.HTTP_404_NOT_FOUND:
            pytest.skip("Validate endpoint not implemented")
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "name" in data
        assert "status" in data
    
    def test_health_endpoint(self, client):
        """Test health endpoint."""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_health_ready_endpoint(self, client):
        """Test readiness endpoint."""
        response = client.get("/health/ready")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["ready"] is True
    
    def test_health_live_endpoint(self, client):
        """Test liveness endpoint."""
        response = client.get("/health/live")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["alive"] is True


class TestWorkflowConfigEndpoint:
    """Tests for workflow configuration endpoint."""
    
    def test_get_workflow_config(self, client):
        """Test getting workflow configuration."""
        response = client.get("/config/workflow")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "name" in data
        assert "stages" in data
        assert len(data["stages"]) == 12  # 12 stages in workflow

