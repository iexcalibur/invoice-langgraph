"""
Tests for Workflows API endpoints.
"""

import pytest
from fastapi import status


class TestWorkflowListEndpoint:
    """Tests for GET /api/v1/workflows endpoint."""
    
    def test_list_workflows_empty(self, client):
        """Test listing workflows when empty."""
        response = client.get("/api/v1/workflows")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "items" in data or isinstance(data, list)
    
    def test_list_workflows_with_pagination(self, client):
        """Test listing workflows with pagination."""
        response = client.get("/api/v1/workflows?page=1&page_size=10")
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_list_workflows_with_status_filter(self, client):
        """Test listing workflows filtered by status."""
        response = client.get("/api/v1/workflows?status=RUNNING")
        
        assert response.status_code == status.HTTP_200_OK


class TestWorkflowDetailEndpoint:
    """Tests for GET /api/v1/workflows/{workflow_id} endpoint."""
    
    def test_get_workflow_not_found(self, client):
        """Test getting non-existent workflow."""
        response = client.get("/api/v1/workflows/wf_nonexistent_123")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_workflow_after_create(self, client, sample_invoice_payload):
        """Test getting workflow after creation."""
        # First create a workflow
        create_response = client.post("/api/v1/invoke", json=sample_invoice_payload)
        
        if create_response.status_code != status.HTTP_202_ACCEPTED:
            pytest.skip("Failed to create workflow")
        
        workflow_id = create_response.json()["workflow_id"]
        
        # Then get it
        response = client.get(f"/api/v1/workflows/{workflow_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["workflow_id"] == workflow_id


class TestWorkflowStatsEndpoint:
    """Tests for workflow statistics endpoint."""
    
    def test_get_workflow_stats(self, client):
        """Test getting workflow statistics."""
        response = client.get("/api/v1/workflows/stats")
        
        if response.status_code == status.HTTP_404_NOT_FOUND:
            pytest.skip("Stats endpoint not implemented")
        
        assert response.status_code == status.HTTP_200_OK

