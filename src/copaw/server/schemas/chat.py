"""
聊天相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime


class BusMessageV3(BaseModel):
    """总线消息 v3"""
    
    message_id: str
    channel_id: str
    channel_type: str
    caller_logical_id: str
    caller_physical_id: str
    called_id: str
    session_id: str
    content_type: Literal["text", "image", "file", "voice", "video"]
    content: str
    timestamp: datetime
    direction: Literal["inbound", "outbound"]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SendMessageRequest(BaseModel):
    """发送消息请求"""
    
    call_id: str
    content: str
    content_type: Literal["text", "image", "file", "voice", "video"] = "text"
    metadata: Optional[Dict[str, Any]] = None


class SendMessageResponse(BaseModel):
    """发送消息响应"""
    
    message_id: str
    call_id: str
    status: Literal["sent", "queued", "failed"]
    timestamp: datetime


class SessionContextV2(BaseModel):
    """会话上下文 v2"""
    
    session_id: str
    channel_id: str
    channel_type: str
    caller_logical_id: str
    caller_physical_id: Optional[str] = None
    called_id: str
    user_profile: Optional[Dict[str, Any]] = None
    group_context: Optional[Dict[str, Any]] = None
    created_at: datetime
    last_message_at: datetime
    message_count: int


class SessionResponse(BaseModel):
    """会话响应"""
    
    session_id: str
    call_id: str
    channel_id: str
    caller_id: str
    called_id: str
    status: Literal["active", "paused", "closed"]
    created_at: datetime
    last_message_at: datetime
    message_count: int
    context: Optional[SessionContextV2] = None


class SessionListResponse(BaseModel):
    """会话列表响应"""
    
    sessions: List[SessionResponse]
    total: int
    page: int
    page_size: int
