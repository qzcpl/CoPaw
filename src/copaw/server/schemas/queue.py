"""
队列相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime


class QueueConfigResponse(BaseModel):
    """队列配置响应"""
    
    queue_id: str
    tenant_id: str
    channel_id: str
    max_size: int
    backend: Literal["redis", "sqlite"]
    status: Literal["active", "paused", "error"]
    created_at: datetime
    updated_at: datetime
    config: Dict[str, Any] = Field(default_factory=dict)


class QueueConfigUpdateRequest(BaseModel):
    """队列配置更新请求"""
    
    max_size: Optional[int] = None
    backend: Optional[Literal["redis", "sqlite"]] = None
    config: Optional[Dict[str, Any]] = None


class QueueStatusResponse(BaseModel):
    """队列状态响应"""
    
    queue_id: str
    current_size: int
    max_size: int
    pending_count: int
    processing_count: int
    failed_count: int
    avg_wait_time_ms: float
    status: Literal["healthy", "warning", "critical"]


class QueueMetricsResponse(BaseModel):
    """队列指标响应"""
    
    queue_id: str
    messages_in_24h: int
    messages_processed_24h: int
    messages_failed_24h: int
    avg_processing_time_ms: float
    p99_latency_ms: float


class MessageTraceResponse(BaseModel):
    """消息追踪响应"""
    
    message_id: str
    queue_id: str
    status: Literal["pending", "processing", "completed", "failed"]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int
    error_message: Optional[str] = None
