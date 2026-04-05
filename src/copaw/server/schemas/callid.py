"""
callId 相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime


class CallIdBindingResponse(BaseModel):
    """callId 绑定响应"""
    
    call_id: str
    call_type: Literal["shared", "dedicated"]
    owner_agent_id: str
    owner_tenant_id: str
    channel_id: str
    channel_instance_id: str
    routing_strategy: Literal["direct", "round_robin", "weighted", "skill_based"]
    routing_config: Dict[str, Any]
    status: Literal["active", "suspended", "unbound"]
    bound_at: datetime
    suspended_at: Optional[datetime] = None
    suspended_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CallIdBindRequest(BaseModel):
    """callId 绑定请求"""
    
    call_id: str
    agent_id: str
    tenant_id: str
    channel_id: str
    routing_strategy: Optional[Literal["direct", "round_robin", "weighted", "skill_based"]] = "direct"
    routing_config: Optional[Dict[str, Any]] = None


class CallIdUnbindRequest(BaseModel):
    """callId 解绑请求"""
    
    call_id: str
    tenant_id: str


class CallIdSwitchRequest(BaseModel):
    """Agent 切换请求"""
    
    call_id: str
    new_agent_id: str
    tenant_id: str
    reason: Optional[str] = None


class CallIdSuspendRequest(BaseModel):
    """callId 暂停请求"""
    
    call_id: str
    tenant_id: str
    reason: str


class CallIdResumeRequest(BaseModel):
    """callId 恢复请求"""
    
    call_id: str
    tenant_id: str


class CallIdChangeRecordResponse(BaseModel):
    """callId 变更记录响应"""
    
    call_id: str
    change_type: Literal["bind", "switch", "suspend", "resume", "unbind"]
    old_binding: Optional[Dict[str, Any]]
    new_binding: Optional[Dict[str, Any]]
    operator: str
    reason: str
    created_at: datetime
