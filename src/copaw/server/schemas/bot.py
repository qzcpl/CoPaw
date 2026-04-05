"""
Bot 相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime


class BotResponse(BaseModel):
    """Bot 响应"""
    
    bot_id: str
    bot_name: str
    tenant_id: str
    platform: Literal["dingtalk", "feishu", "wechat", "web"]
    status: Literal["connected", "disconnected", "error"]
    webhook_url: Optional[str] = None
    client_id: Optional[str] = None
    connected_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    config: Dict[str, Any] = Field(default_factory=dict)


class BotCreateRequest(BaseModel):
    """Bot 创建请求"""
    
    bot_name: str
    platform: Literal["dingtalk", "feishu", "wechat", "web"]
    tenant_id: str
    config: Dict[str, Any] = Field(default_factory=dict)


class BotUpdateRequest(BaseModel):
    """Bot 更新请求"""
    
    bot_name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class BotConnectRequest(BaseModel):
    """Bot 连接请求"""
    
    bot_id: str
    client_id: str
    client_secret: str
    webhook_url: str


class BotStatusResponse(BaseModel):
    """Bot 状态响应"""
    
    bot_id: str
    status: Literal["connected", "disconnected", "error"]
    last_heartbeat: Optional[datetime] = None
    message_count: int
    error_count: int
