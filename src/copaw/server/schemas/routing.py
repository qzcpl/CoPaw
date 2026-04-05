"""
路由相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime


class RoutingStrategyResponse(BaseModel):
    """路由策略响应"""
    
    strategy_id: str
    strategy_name: str
    strategy_type: Literal["direct", "round_robin", "weighted", "skill_based", "least_loaded"]
    tenant_id: str
    config: Dict[str, Any] = Field(default_factory=dict)
    status: Literal["active", "inactive"]
    created_at: datetime
    updated_at: datetime


class RoutingStrategyCreateRequest(BaseModel):
    """路由策略创建请求"""
    
    strategy_name: str
    strategy_type: Literal["direct", "round_robin", "weighted", "skill_based", "least_loaded"]
    tenant_id: str
    config: Dict[str, Any] = Field(default_factory=dict)


class RoutingStrategyUpdateRequest(BaseModel):
    """路由策略更新请求"""
    
    strategy_name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    status: Optional[Literal["active", "inactive"]] = None


class RoutingConfigResponse(BaseModel):
    """路由配置响应"""
    
    call_id: str
    strategy_id: str
    strategy_type: str
    config: Dict[str, Any]
    targets: List[Dict[str, Any]]
    status: Literal["active", "inactive"]


class RoutingConfigUpdateRequest(BaseModel):
    """路由配置更新请求"""
    
    strategy_id: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    targets: Optional[List[Dict[str, Any]]] = None
