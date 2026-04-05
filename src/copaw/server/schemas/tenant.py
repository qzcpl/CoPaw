"""
租户相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class TenantResponse(BaseModel):
    """租户响应"""
    
    tenant_id: str
    tenant_name: str
    status: str
    created_at: datetime
    updated_at: datetime
    config: Dict[str, Any] = Field(default_factory=dict)
    max_agents: int
    max_callids: int


class TenantCreateRequest(BaseModel):
    """租户创建请求"""
    
    tenant_id: str
    tenant_name: str
    max_agents: int = 10
    max_callids: int = 100
    config: Dict[str, Any] = Field(default_factory=dict)


class TenantUpdateRequest(BaseModel):
    """租户更新请求"""
    
    tenant_name: Optional[str] = None
    max_agents: Optional[int] = None
    max_callids: Optional[int] = None
    config: Optional[Dict[str, Any]] = None


class TenantStatsResponse(BaseModel):
    """租户统计响应"""
    
    tenant_id: str
    agent_count: int
    callid_count: int
    message_count_24h: int
    active_sessions: int
