# -*- coding: utf-8 -*-
"""Tenant management API routes."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tenants", tags=["tenants"])


TENANTS_DB: Dict[str, Dict[str, Any]] = {
    "default": {
        "tenant_id": "default",
        "tenant_name": "Default Tenant",
        "status": "active",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "config": {},
        "max_agents": 10,
        "max_callids": 100,
    },
}


class TenantResponse(BaseModel):
    """Tenant response."""

    tenant_id: str
    tenant_name: str
    status: Literal["active", "inactive"]
    created_at: str
    updated_at: str
    config: Dict[str, Any]
    max_agents: Optional[int] = None
    max_callids: Optional[int] = None


class TenantCreateRequest(BaseModel):
    """Tenant create request."""

    tenant_id: str
    tenant_name: str
    status: Literal["active", "inactive"] = "active"
    max_agents: Optional[int] = 10
    max_callids: Optional[int] = None
    config: Optional[Dict[str, Any]] = None


class TenantUpdateRequest(BaseModel):
    """Tenant update request."""

    tenant_name: Optional[str] = None
    status: Optional[Literal["active", "inactive"]] = None
    max_agents: Optional[int] = None
    max_callids: Optional[int] = None
    config: Optional[Dict[str, Any]] = None


class TenantStatsResponse(BaseModel):
    """Tenant stats response."""

    tenant_id: str
    agent_count: int
    callid_count: int
    message_count: int
    error_count: int
    stats_at: str


def _get_current_user(request: Request) -> Dict[str, str]:
    """Get current user from request state."""
    user = getattr(request.state, "user", None)
    if not user:
        return {
            "user_id": "default",
            "tenant_id": "default",
            "role": "system_admin",
        }
    return {
        "user_id": user,
        "tenant_id": "default",
        "role": "system_admin",
    }


@router.get("", response_model=List[TenantResponse])
async def list_tenants(
    request: Request,
    tenant_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    """List tenants."""
    _get_current_user(request)
    tenants = list(TENANTS_DB.values())
    if tenant_id:
        tenants = [t for t in tenants if t.get("tenant_id") == tenant_id]
    if status:
        tenants = [t for t in tenants if t.get("status") == status]
    return tenants


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    request: Request,
    tenant_id: str,
) -> Dict[str, Any]:
    """Get tenant details."""
    _get_current_user(request)
    tenant = TENANTS_DB.get(tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=404,
            detail=f"Tenant not found: {tenant_id}",
        )
    return tenant


@router.post("", response_model=TenantResponse)
async def create_tenant(
    request: Request,
    data: TenantCreateRequest,
) -> Dict[str, Any]:
    """Create tenant."""
    _get_current_user(request)
    if data.tenant_id in TENANTS_DB:
        raise HTTPException(
            status_code=400,
            detail=f"Tenant already exists: {data.tenant_id}",
        )
    tenant = {
        "tenant_id": data.tenant_id,
        "tenant_name": data.tenant_name,
        "status": data.status,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "config": data.config or {},
        "max_agents": data.max_agents,
        "max_callids": data.max_callids,
    }
    TENANTS_DB[data.tenant_id] = tenant
    return tenant


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    request: Request,
    tenant_id: str,
    data: TenantUpdateRequest,
) -> Dict[str, Any]:
    """Update tenant."""
    _get_current_user(request)
    tenant = TENANTS_DB.get(tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=404,
            detail=f"Tenant not found: {tenant_id}",
        )
    if data.tenant_name:
        tenant["tenant_name"] = data.tenant_name
    if data.max_agents is not None:
        tenant["max_agents"] = data.max_agents
    if data.max_callids is not None:
        tenant["max_callids"] = data.max_callids
    if data.config:
        tenant["config"] = data.config
    tenant["updated_at"] = datetime.utcnow().isoformat() + "Z"
    return tenant


@router.delete("/{tenant_id}")
async def delete_tenant(
    request: Request,
    tenant_id: str,
) -> Dict[str, str]:
    """Delete tenant."""
    _get_current_user(request)
    if tenant_id not in TENANTS_DB:
        raise HTTPException(
            status_code=404,
            detail=f"Tenant not found: {tenant_id}",
        )
    if tenant_id == "default":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete default tenant",
        )
    del TENANTS_DB[tenant_id]
    return {"message": "Tenant deleted successfully"}


@router.get("/{tenant_id}/stats", response_model=TenantStatsResponse)
async def get_tenant_stats(
    request: Request,
    tenant_id: str,
) -> Dict[str, Any]:
    """Get tenant stats."""
    _get_current_user(request)
    if tenant_id not in TENANTS_DB:
        raise HTTPException(
            status_code=404,
            detail=f"Tenant not found: {tenant_id}",
        )
    return {
        "tenant_id": tenant_id,
        "agent_count": 0,
        "callid_count": 0,
        "message_count": 0,
        "error_count": 0,
        "stats_at": datetime.utcnow().isoformat() + "Z",
    }
