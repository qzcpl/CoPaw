"""
路由配置 API
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime

from ..schemas.routing import (
    RoutingStrategyResponse,
    RoutingStrategyCreateRequest,
    RoutingStrategyUpdateRequest,
    RoutingConfigResponse,
    RoutingConfigUpdateRequest,
)
from ..core.exceptions import ApiError, ApiErrorCode
from ..dependencies import get_current_user

router = APIRouter()

# 模拟路由策略数据库
ROUTING_STRATEGIES_DB = {}
ROUTING_CONFIGS_DB = {}


@router.get("/strategies", response_model=List[RoutingStrategyResponse])
async def list_routing_strategies(
    tenant_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    列出路由策略
    
    Args:
        tenant_id: 租户 ID
        current_user: 当前用户
    
    Returns:
        路由策略列表
    """
    effective_tenant_id = tenant_id or current_user["tenant_id"]
    
    strategies = [s for s in ROUTING_STRATEGIES_DB.values() if s["tenant_id"] == effective_tenant_id]
    
    return strategies


@router.post("/strategies", response_model=RoutingStrategyResponse)
async def create_routing_strategy(
    request: RoutingStrategyCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    创建路由策略
    
    Args:
        request: 创建请求
        current_user: 当前用户
    
    Returns:
        创建的路由策略
    """
    # 权限检查
    if current_user["role"] not in ["tenant_admin", "system_admin"]:
        raise ApiError(
            code=ApiErrorCode.PERMISSION_DENIED,
            message="Only tenant admin can create routing strategy",
            status_code=403,
        )
    
    strategy_id = f"strategy_{request.strategy_name}_{int(datetime.utcnow().timestamp())}"
    
    strategy = {
        "strategy_id": strategy_id,
        "strategy_name": request.strategy_name,
        "strategy_type": request.strategy_type,
        "tenant_id": request.tenant_id,
        "config": request.config,
        "status": "active",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }
    
    ROUTING_STRATEGIES_DB[strategy_id] = strategy
    
    return strategy


@router.put("/strategies/{strategy_id}", response_model=RoutingStrategyResponse)
async def update_routing_strategy(
    strategy_id: str,
    request: RoutingStrategyUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    更新路由策略
    
    Args:
        strategy_id: 路由策略 ID
        request: 更新请求
        current_user: 当前用户
    
    Returns:
        更新后的路由策略
    """
    strategy = ROUTING_STRATEGIES_DB.get(strategy_id)
    
    if not strategy:
        raise ApiError(
            code=ApiErrorCode.ROUTING_STRATEGY_NOT_FOUND,
            message=f"Routing strategy not found: {strategy_id}",
            status_code=404,
        )
    
    # 更新字段
    if request.strategy_name:
        strategy["strategy_name"] = request.strategy_name
    if request.config:
        strategy["config"] = request.config
    if request.status:
        strategy["status"] = request.status
    strategy["updated_at"] = datetime.utcnow().isoformat() + "Z"
    
    return strategy


@router.get("/config/{call_id}", response_model=RoutingConfigResponse)
async def get_routing_config(
    call_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    查询路由配置
    
    Args:
        call_id: callId
        current_user: 当前用户
    
    Returns:
        路由配置
    """
    config = ROUTING_CONFIGS_DB.get(call_id)
    
    if not config:
        raise ApiError(
            code=ApiErrorCode.ROUTING_STRATEGY_NOT_FOUND,
            message=f"Routing config not found for callId: {call_id}",
            status_code=404,
        )
    
    return config


@router.put("/config/{call_id}", response_model=RoutingConfigResponse)
async def update_routing_config(
    call_id: str,
    request: RoutingConfigUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    更新路由配置
    
    Args:
        call_id: callId
        request: 更新请求
        current_user: 当前用户
    
    Returns:
        更新后的路由配置
    """
    # 权限检查
    if current_user["role"] not in ["tenant_admin", "system_admin"]:
        raise ApiError(
            code=ApiErrorCode.PERMISSION_DENIED,
            message="Only tenant admin can update routing config",
            status_code=403,
        )
    
    config = ROUTING_CONFIGS_DB.get(call_id)
    
    if not config:
        # 创建新配置
        config = {
            "call_id": call_id,
            "strategy_id": request.strategy_id or "default",
            "strategy_type": "direct",
            "config": request.config or {},
            "targets": request.targets or [],
            "status": "active",
        }
    
    # 更新字段
    if request.strategy_id:
        config["strategy_id"] = request.strategy_id
    if request.config:
        config["config"] = request.config
    if request.targets:
        config["targets"] = request.targets
    
    ROUTING_CONFIGS_DB[call_id] = config
    
    return config
