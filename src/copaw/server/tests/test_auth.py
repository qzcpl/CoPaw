"""
Test authentication API
"""
import pytest
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "2.0.0"


def test_root_endpoint(client: TestClient):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "CoPaw API"
    assert data["version"] == "2.0.0"


def test_login_success(client: TestClient):
    """Test successful login"""
    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "admin123456",
            "tenant_id": "default",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["token_type"] == "bearer"
    assert data["user_id"] == "user_admin"
    assert data["tenant_id"] == "default"
    assert data["role"] == "system_admin"


def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials"""
    response = client.post(
        "/auth/login",
        json={
            "username": "invalid_user",
            "password": "wrong_password",
            "tenant_id": "default",
        }
    )
    assert response.status_code == 401
    data = response.json()
    assert data["code"] == "AUTH_FAILED"


def test_login_wrong_tenant(client: TestClient):
    """Test login with wrong tenant"""
    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "admin123456",
            "tenant_id": "wrong_tenant",
        }
    )
    assert response.status_code == 403
    data = response.json()
    assert data["code"] == "TENANT_ACCESS_DENIED"


def test_register_success(client: TestClient):
    """Test successful registration"""
    response = client.post(
        "/auth/register",
        json={
            "username": "test_user",
            "password": "test_password_123",
            "tenant_id": "default",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["user_id"].startswith("user_test_user_")
    assert data["tenant_id"] == "default"
    assert data["role"] == "user"


def test_register_duplicate_username(client: TestClient):
    """Test registration with duplicate username"""
    # First registration
    client.post(
        "/auth/register",
        json={
            "username": "duplicate_user",
            "password": "test_password_123",
            "tenant_id": "default",
        }
    )
    
    # Second registration with same username
    response = client.post(
        "/auth/register",
        json={
            "username": "duplicate_user",
            "password": "test_password_123",
            "tenant_id": "default",
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "AUTH_FAILED"


def test_get_current_user(client: TestClient, auth_headers: dict):
    """Test get current user info"""
    response = client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user_admin"
    assert data["tenant_id"] == "default"
    assert data["role"] == "system_admin"


def test_get_current_user_unauthorized(client: TestClient):
    """Test get current user without authentication"""
    response = client.get("/auth/me")
    assert response.status_code == 401
