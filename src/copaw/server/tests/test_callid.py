"""
Test callId management API
"""
import pytest
from fastapi.testclient import TestClient


def test_list_callid_bindings(client: TestClient, auth_headers: dict):
    """Test list callId bindings"""
    response = client.get("/callid/bindings", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_callid_binding(client: TestClient, auth_headers: dict):
    """Test get callId binding"""
    response = client.get("/callid/bindings/400-001", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["call_id"] == "400-001"
    assert data["status"] == "active"


def test_get_callid_not_found(client: TestClient, auth_headers: dict):
    """Test get non-existent callId"""
    response = client.get("/callid/bindings/non-existent", headers=auth_headers)
    assert response.status_code == 404
    data = response.json()
    assert data["code"] == "CALLID_NOT_FOUND"


def test_bind_callid_success(client: TestClient, auth_headers: dict):
    """Test successful callId binding"""
    response = client.post(
        "/callid/bind",
        headers=auth_headers,
        json={
            "call_id": "test-001",
            "agent_id": "agent_test",
            "tenant_id": "default",
            "channel_id": "dingtalk",
            "routing_strategy": "direct",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["call_id"] == "test-001"
    assert data["owner_agent_id"] == "agent_test"
    assert data["status"] == "active"


def test_bind_callid_duplicate(client: TestClient, auth_headers: dict):
    """Test binding duplicate callId"""
    # First binding
    client.post(
        "/callid/bind",
        headers=auth_headers,
        json={
            "call_id": "test-duplicate",
            "agent_id": "agent_test",
            "tenant_id": "default",
            "channel_id": "dingtalk",
        }
    )
    
    # Second binding with same callId
    response = client.post(
        "/callid/bind",
        headers=auth_headers,
        json={
            "call_id": "test-duplicate",
            "agent_id": "agent_test_2",
            "tenant_id": "default",
            "channel_id": "dingtalk",
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "CALLID_ALREADY_BOUND"


def test_switch_agent(client: TestClient, auth_headers: dict):
    """Test agent switch"""
    response = client.post(
        "/callid/switch",
        headers=auth_headers,
        json={
            "call_id": "400-001",
            "new_agent_id": "agent_new",
            "tenant_id": "default",
            "reason": "Test switch",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Agent switched successfully"
    
    # Verify switch
    response = client.get("/callid/bindings/400-001", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["owner_agent_id"] == "agent_new"


def test_suspend_callid(client: TestClient, auth_headers: dict):
    """Test suspend callId"""
    response = client.post(
        "/callid/bindings/400-001/suspend",
        headers=auth_headers,
        json={
            "call_id": "400-001",
            "tenant_id": "default",
            "reason": "Test suspend",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "callId suspended successfully"
    
    # Verify suspend
    response = client.get("/callid/bindings/400-001", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "suspended"
    assert data["suspended_reason"] == "Test suspend"


def test_resume_callid(client: TestClient, auth_headers: dict):
    """Test resume callId"""
    # First suspend
    client.post(
        "/callid/bindings/400-001/suspend",
        headers=auth_headers,
        json={
            "call_id": "400-001",
            "tenant_id": "default",
            "reason": "Test suspend",
        }
    )
    
    # Then resume
    response = client.post(
        "/callid/bindings/400-001/resume",
        headers=auth_headers,
        json={
            "call_id": "400-001",
            "tenant_id": "default",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "callId resumed successfully"
    
    # Verify resume
    response = client.get("/callid/bindings/400-001", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert data["suspended_reason"] is None


def test_get_callid_history(client: TestClient, auth_headers: dict):
    """Test get callId history"""
    response = client.get(
        "/callid/history?call_id=400-001&tenant_id=default",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
