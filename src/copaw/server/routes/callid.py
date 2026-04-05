"""
callId 管理 API
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime

from ..schemas.callid import (
    CallIdBindingResponse,
    CallIdBindRequest,
    CallIdSwitchRequest,
    CallIdChangeRecordResponse,
    CallIdUnbindRequest,
    CallIdSuspendRequest,
    CallIdResumeRequest,
)
from ..core.exceptions import ApiError, ApiErrorCode
from ..dependencies import get_current_user

router = APIRouter()

# 模拟 callId 数据库（实际实现应使用数据库）
CALLID_DB = {
    "400-001": {
        "call_id": "400-001",
        "call_type": "shared",
        "owner_agent_id": "agent_1",
        "owner_tenant_id": "default",
        "channel_id": "dingtalk",
        "channel_instance_id": "dingtalk_001",
        "routing_strategy": "direct",
        "routing_config": {},
        "status": "active",
        "bound_at": "2026-03-31T10:00:00Z",
        "suspended_at": None,
        "suspended_reason": None,
        "metadata": {},
    }
}

# 变更记录
CALLID_HISTORY = []


@router.get("/bindings", response_model=List[CallIdBindingResponse])
async def list_callid_bindings(
    tenant_id: Optional[str] = Query(None, description="租户 ID"),
    current_user: dict = Depends(get_current_user),
):
    """
    列出 callId 绑定列表
    
    Args:
        tenant_id: 租户 ID（可选，默认使用当前用户租户）
        current_user: 当前用户
    
    Returns:
        callId 绑定列表
    """
    # 使用当前用户租户 ID（如果未指定）
    effective_tenant_id = tenant_id or current_user["tenant_id"]
    
    # 过滤租户
    bindings = [
        b for b in CALLID_DB.values()
        if b["owner_tenant_id"] == effective_tenant_id
    ]
    
    return bindings


@router.get("/bindings/{call_id}", response_model=CallIdBindingResponse)
async def get_callid_binding(
    call_id: str,
    tenant_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    查询 callId 详情
    
    Args:
        call_id: callId
        tenant_id: 租户 ID
        current_user: 当前用户
    
    Returns:
        callId 绑定详情
    """
    # 查询
    binding = CALLID_DB.get(call_id)
    
    if not binding:
        raise ApiError(
            code=ApiErrorCode.CALLID_NOT_FOUND,
            message=f"callId not found: {call_id}",
            status_code=404,
        )
    
    # 权限检查
    effective_tenant_id = tenant_id or current_user["tenant_id"]
    if binding["owner_tenant_id"] != effective_tenant_id:
        raise ApiError(
            code=ApiErrorCode.TENANT_ACCESS_DENIED,
            message="Access denied to this callId",
            status_code=403,
        )
    
    return binding


@router.post("/bind", response_model=CallIdBindingResponse)
async def bind_callid(
    request: CallIdBindRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    绑定 callId
    
    Args:
        request: 绑定请求
        current_user: 当前用户
    
    Returns:
        绑定后的 callId 信息
    """
    # 权限检查（仅租户管理员）
    if current_user["role"] not in ["tenant_admin", "system_admin"]:
        raise ApiError(
            code=ApiErrorCode.PERMISSION_DENIED,
            message="Only tenant admin can bind callId",
            status_code=403,
        )
    
    # 检查 callId 是否已被绑定
    if request.call_id in CALLID_DB:
        raise ApiError(
            code=ApiErrorCode.CALLID_ALREADY_BOUND,
            message=f"callId already bound: {request.call_id}",
            status_code=400,
        )
    
    # 创建绑定
    binding = {
        "call_id": request.call_id,
        "call_type": "shared",
        "owner_agent_id": request.agent_id,
        "owner_tenant_id": request.tenant_id,
        "channel_id": request.channel_id,
        "channel_instance_id": f"{request.channel_id}_{request.call_id}",
        "routing_strategy": request.routing_strategy or "direct",
        "routing_config": request.routing_config or {},
        "status": "active",
        "bound_at": datetime.utcnow().isoformat() + "Z",
        "suspended_at": None,
        "suspended_reason": None,
        "metadata": {},
    }
    
    CALLID_DB[request.call_id] = binding
    
    # 记录变更历史
    CALLID_HISTORY.append({
        "call_id": request.call_id,
        "change_type": "bind",
        "old_binding": None,
        "new_binding": binding,
        "operator": current_user["user_id"],
        "reason": "Initial binding",
        "created_at": datetime.utcnow().isoformat() + "Z",
    })
    
    return binding


@router.post("/unbind")
async def unbind_callid(
    request: CallIdUnbindRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    解绑 callId
    
    Args:
        request: 解绑请求
        current_user: 当前用户
    """
    # 权限检查
    if current_user["role"] not in ["tenant_admin", "system_admin"]:
        raise ApiError(
            code=ApiErrorCode.PERMISSION_DENIED,
            message="Only tenant admin can unbind callId",
            status_code=403,
        )
    
    # 查询绑定
    binding = CALLID_DB.get(request.call_id)
    
    if not binding:
        raise ApiError(
            code=ApiErrorCode.CALLID_NOT_FOUND,
            message=f"callId not found: {request.call_id}",
            status_code=404,
        )
    
    # 权限检查
    if binding["owner_tenant_id"] != request.tenant_id:
        raise ApiError(
            code=ApiErrorCode.TENANT_ACCESS_DENIED,
            message="Access denied to this callId",
            status_code=403,
        )
    
    # 删除绑定
    old_binding = CALLID_DB.pop(request.call_id)
    
    # 记录变更历史
    CALLID_HISTORY.append({
        "call_id": request.call_id,
        "change_type": "unbind",
        "old_binding": old_binding,
        "new_binding": None,
        "operator": current_user["user_id"],
        "reason": "Unbind callId",
        "created_at": datetime.utcnow().isoformat() + "Z",
    })
    
    return {"message": "callId unbound successfully"}


@router.post("/switch")
async def switch_agent(
    request: CallIdSwitchRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    切换 Agent（携号转网）
    
    Args:
        request: 切换请求
        current_user: 当前用户
    """
    # 权限检查
    if current_user["role"] not in ["tenant_admin", "system_admin"]:
        raise ApiError(
            code=ApiErrorCode.PERMISSION_DENIED,
            message="Only tenant admin can switch agent",
            status_code=403,
        )
    
    # 查询当前绑定
    binding = CALLID_DB.get(request.call_id)
    
    if not binding:
        raise ApiError(
            code=ApiErrorCode.CALLID_NOT_FOUND,
            message=f"callId not found: {request.call_id}",
            status_code=404,
        )
    
    # 保存旧绑定
    old_binding = binding.copy()
    
    # 更新绑定
    binding["owner_agent_id"] = request.new_agent_id
    binding["updated_at"] = datetime.utcnow().isoformat() + "Z"
    
    # 记录变更历史
    CALLID_HISTORY.append({
        "call_id": request.call_id,
        "change_type": "switch",
        "old_binding": old_binding,
        "new_binding": binding,
        "operator": current_user["user_id"],
        "reason": request.reason or "Agent switch",
        "created_at": datetime.utcnow().isoformat() + "Z",
    })
    
    return {"message": "Agent switched successfully"}


@router.post("/bindings/{call_id}/suspend")
async def suspend_callid(
    call_id: str,
    request: CallIdSuspendRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    暂停 callId
    
    Args:
        call_id: callId
        request: 暂停请求
        current_user: 当前用户
    """
    # 权限检查
    if current_user["role"] not in ["tenant_admin", "system_admin"]:
        raise ApiError(
            code=ApiErrorCode.PERMISSION_DENIED,
            message="Only tenant admin can suspend callId",
            status_code=403,
        )
    
    # 查询绑定
    binding = CALLID_DB.get(call_id)
    
    if not binding:
        raise ApiError(
            code=ApiErrorCode.CALLID_NOT_FOUND,
            message=f"callId not found: {call_id}",
            status_code=404,
        )
    
    # 更新状态
    binding["status"] = "suspended"
    binding["suspended_at"] = datetime.utcnow().isoformat() + "Z"
    binding["suspended_reason"] = request.reason
    
    # 记录变更历史
    CALLID_HISTORY.append({
        "call_id": call_id,
        "change_type": "suspend",
        "old_binding": binding.copy(),
        "new_binding": binding,
        "operator": current_user["user_id"],
        "reason": request.reason,
        "created_at": datetime.utcnow().isoformat() + "Z",
    })
    
    return {"message": "callId suspended successfully"}


@router.post("/bindings/{call_id}/resume")
async def resume_callid(
    call_id: str,
    request: CallIdResumeRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    恢复 callId
    
    Args:
        call_id: callId
        request: 恢复请求
        current_user: 当前用户
    """
    # 权限检查
    if current_user["role"] not in ["tenant_admin", "system_admin"]:
        raise ApiError(
            code=ApiErrorCode.PERMISSION_DENIED,
            message="Only tenant admin can resume callId",
            status_code=403,
        )
    
    # 查询绑定
    binding = CALLID_DB.get(call_id)
    
    if not binding:
        raise ApiError(
            code=ApiErrorCode.CALLID_NOT_FOUND,
            message=f"callId not found: {call_id}",
            status_code=404,
        )
    
    # 更新状态
    binding["status"] = "active"
    binding["suspended_at"] = None
    binding["suspended_reason"] = None
    
    # 记录变更历史
    CALLID_HISTORY.append({
        "call_id": call_id,
        "change_type": "resume",
        "old_binding": binding.copy(),
        "new_binding": binding,
        "operator": current_user["user_id"],
        "reason": "Resume callId",
        "created_at": datetime.utcnow().isoformat() + "Z",
    })
    
    return {"message": "callId resumed successfully"}


@router.get("/history", response_model=List[CallIdChangeRecordResponse])
async def get_callid_history(
    call_id: str = Query(...),
    tenant_id: str = Query(...),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    """
    查询 callId 变更历史
    
    Args:
        call_id: callId
        tenant_id: 租户 ID
        limit: 返回记录数
        current_user: 当前用户
    
    Returns:
        变更历史记录
    """
    # 过滤
    history = [
        h for h in CALLID_HISTORY
        if h["call_id"] == call_id
    ]
    
    # 按时间倒序，限制数量
    history = sorted(history, key=lambda x: x["created_at"], reverse=True)[:limit]
    
    return history
