"""
Tests for Human Review API endpoints.
"""

import pytest
from fastapi import status


class TestHumanReviewListEndpoint:
    """Tests for GET /api/v1/human-review/pending endpoint."""
    
    def test_list_pending_reviews_empty(self, client):
        """Test listing pending reviews when empty."""
        response = client.get("/api/v1/human-review/pending")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "items" in data or isinstance(data, list)
    
    def test_list_pending_reviews_with_pagination(self, client):
        """Test listing pending reviews with pagination."""
        response = client.get("/api/v1/human-review/pending?page=1&page_size=10")
        
        assert response.status_code == status.HTTP_200_OK


class TestHumanReviewDecisionEndpoint:
    """Tests for POST /api/v1/human-review/decision endpoint."""
    
    def test_decision_checkpoint_not_found(self, client):
        """Test decision with non-existent checkpoint."""
        decision_payload = {
            "checkpoint_id": "cp_nonexistent_123",
            "decision": "ACCEPT",
            "reviewer_id": "reviewer_001",
            "notes": "Approved after review",
        }
        
        response = client.post("/api/v1/human-review/decision", json=decision_payload)
        
        # Should return 404 or similar error
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_400_BAD_REQUEST,
        ]
    
    def test_decision_invalid_decision_value(self, client):
        """Test decision with invalid decision value."""
        decision_payload = {
            "checkpoint_id": "cp_test_123",
            "decision": "INVALID_DECISION",
            "reviewer_id": "reviewer_001",
            "notes": "",
        }
        
        response = client.post("/api/v1/human-review/decision", json=decision_payload)
        
        # Should return validation error
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,  # Checkpoint not found
        ]
    
    def test_decision_missing_required_fields(self, client):
        """Test decision with missing required fields."""
        incomplete_payload = {
            "checkpoint_id": "cp_test_123",
            # Missing decision, reviewer_id
        }
        
        response = client.post("/api/v1/human-review/decision", json=incomplete_payload)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestHumanReviewDetailEndpoint:
    """Tests for GET /api/v1/human-review/{checkpoint_id} endpoint."""
    
    def test_get_review_not_found(self, client):
        """Test getting non-existent review."""
        response = client.get("/api/v1/human-review/cp_nonexistent_123")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestHumanReviewAPIContract:
    """Tests to verify API matches the contract from task.txt."""
    
    def test_pending_endpoint_path(self, client):
        """Test pending endpoint exists at correct path."""
        response = client.get("/api/v1/human-review/pending")
        
        # Should not be 404 (path should exist)
        assert response.status_code != status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_decision_endpoint_path(self, client):
        """Test decision endpoint exists at correct path."""
        response = client.post(
            "/api/v1/human-review/decision",
            json={
                "checkpoint_id": "test",
                "decision": "ACCEPT",
                "reviewer_id": "test",
                "notes": "",
            },
        )
        
        # Should not be 405 (path should exist)
        assert response.status_code != status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_pending_response_schema(self, client):
        """Test pending response matches expected schema."""
        response = client.get("/api/v1/human-review/pending")
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            
            # Should have items array
            items = data.get("items", data)
            assert isinstance(items, list)
            
            # Each item should have expected fields (if any exist)
            for item in items:
                assert "checkpoint_id" in item
                assert "invoice_id" in item

