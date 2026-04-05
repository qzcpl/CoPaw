"""
pytest configuration for CoPaw Server tests
"""
import pytest
from fastapi.testclient import TestClient
from ..main import app


@pytest.fixture
def client():
    """Create test client"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client):
    """Get authentication headers"""
    # Login to get token
    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "admin123456",
            "tenant_id": "default",
        }
    )
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}
