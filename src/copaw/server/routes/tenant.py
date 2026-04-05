"""
租户管理 API
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime

from ..schemas.tenant import (
    TenantResponse,
    TenantCreateRequest,
    TenantUpdateRequest,
    TenantStatsResponse,
)
from ..core.exceptions import ApiError, ApiErrorCode
from ..dependencies import get_current_user

router = APIRouter()

# 模拟租户数据库
TENANTS_DB = {
    "default": {
        "tenant_id": "default",
        "tenant_name": "Default Tenant",
        "status": "active",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
        "config": {},
        "max_agents": 10,
        "max_callids": 100,
    }
}


@router.get("", response_model=List[TenantResponse])
async def list_tenants(
    current_user: dict = Depends(get_current_user),
):
    """
    列出租户列表
    
    Args:
        current_user: 当前用户
    
    Returns:
        租户列表
    """
    # 仅系统管理员可查看所有租户
    if current_user["role"] != "system_admin":
        # 普通用户只能查看自己的租户
        tenant = TENANTS_DB.get(current_user["tenant_id"])
        if not tenant:
            return []
        return [tenant]
    
    return list(TENANTS_DB.values())


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    查询租户详情
    
    Args:
        tenant_id: 租户 ID
        current_user: 当前用户
    
    Returns:
        租户详情
    """
    # 权限检查
    if current_user["role"] not in ["system_admin"] and current_user["tenant_id"] != tenant_id:
        raise ApiError(
            code=ApiErrorCode.TENANT_ACCESS_DENIED,
            message="Access denied to this tenant",
            status_code=403,
        )
    
    tenant = TENANTS_DB.get(tenant_id)
    
    if not tenant:
        raise ApiError(
            code=ApiErrorCode.TENANT_NOT_FOUND,
            message=f"Tenant not found: {tenant_id}",
            status_code=404,
        )
    
    return tenant


@router.post("", response_model=TenantResponse)
async def create_tenant(
    request: TenantCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    创建租户
    
    Args:
        request: 创建请求
        current_user: 当前用户
    
    Returns:
        创建的租户
    """
    # 仅系统管理员可创建租户
    if current_user["role"] != "system_admin":
        raise ApiError(
            code=ApiErrorCode.PERMISSION_DENIED,
            message="Only system admin can create tenant",
            status_code=403,
        )
    
    # 检查是否已存在
    if request.tenant_id in TENANTS_DB:
        raise ApiError(
            code=ApiErrorCode.TENANT_ALREADY_EXISTS,
            message=f"Tenant already exists: {request.tenant_id}",
            status_code=400,
        )
    
    tenant = {
        "tenant_id": request.tenant_id,
        "tenant_name": request.tenant_name,
        "status": "active",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "config": request.config,
        "max_agents": request.max_agents,
        "max_callids": request.max_callids,
    }
    
    TENANTS_DB[request.tenant_id] = tenant
    
    return tenant


@router.put("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: str,
    request: TenantUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    更新租户
    
    Args:
        tenant_id: 租户 ID
        request: 更新请求
        current_user: 当前用户
    
    Returns:
        更新后的租户
    """
    # 仅系统管理员可更新租户
    if current_user["role"] != "system_admin":
        raise ApiError(
            code=ApiErrorCode.PERMISSION_DENIED,
            message="Only system admin can update tenant",
            status_code=403,
        )
    
    tenant = TENANTS_DB.get(tenant_id)
    
    if not tenant:
        raise ApiError(
            code=ApiErrorCode.TENANT_NOT_FOUND,
            message=f"Tenant not found: {tenant_id}",
            status_code=404,
        )
    
    # 更新字段
    if request.tenant_name:
        tenant["tenant_name"] = request.tenant_name
    if request.max_agents:
        tenant["max_agents"] = request.max_agents
    if request.max_callids:
        tenant["max_callids"] = request.max_callids
    if request.config:
        tenant["config"] = request.config
    tenant["updated_at"] = datetime.utcnow().isoformat() + "Z"
    
    return tenant


@router.delete("/{tenant_id}")
async def delete_tenant(
    tenant_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    删除租户
    
    Args:
        tenant_id: 租户 ID
        current_user: 当前用户
    """
    # 仅系统管理员可删除租户
    if current_user["role"] != "system_admin":
        raise ApiError(
            code=ApiErrorCode.PERMISSION_DENIED,
            message="Only system admin can delete tenant",
            status_code=403,
        )
    
    if tenant_id not in TENANTS_DB:
        raise ApiError(
            code=ApiErrorCode.TENANT_NOT_FOUND,
            message=f"Tenant not found: {tenant_id}",
            status_code=404,
        )
    
    # 不允许删除默认租户
    if tenant_id == "default":
        raise ApiError(
            code=ApiErrorCode.INVALID_PARAMS,
            message="Cannot delete default tenant",
            status_code=400,
        )
    
    del TENANTS_DB[tenant_id]
    
    return {"message": "Tenant deleted successfully"}


@router.get("/{tenant_id}/stats", response_model=TenantStatsResponse)
async def get_tenant_stats(
    tenant_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    查询租户统计
    
    Args:
        tenant_id: 租户 ID
        current_user: 当前用户
    
    Returns:
        租户统计
    """
    # 权限检查
    if current_user["role"] not in ["system_admin"] and current_user["tenant_id"] != tenant_id:
        raise ApiError(
            code=ApiErrorCode.TENANT_ACCESS_DENIED,
            message="Access denied to this tenant",
            status_code=403,
        )
    
    tenant = TENANTS_DB.get(tenant_id)
    
    if not tenant:
        raise ApiError(
            code=ApiErrorCode.TENANT_NOT_FOUND,
            message=f"Tenant not found: {tenant_id}",
            status_code=404,
        )
    
    # TODO: 实现真实统计
    return TenantStatsResponse(
        tenant_id=tenant_id,
        agent_count=0,
        callid_count=0,
        message_count_24h=0,
        active_sessions=0,
    )
