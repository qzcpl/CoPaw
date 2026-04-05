"""
灰度发布相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime


class GrayReleaseConfigResponse(BaseModel):
    """灰度发布配置响应"""
    
    release_id: str
    release_name: str
    call_id: str
    target_agent_id: str
    traffic_percentage: int
    status: Literal["active", "paused", "completed", "rolled_back"]
    started_at: datetime
    completed_at: Optional[datetime] = None
    config: Dict[str, Any] = Field(default_factory=dict)


class GrayReleaseCreateRequest(BaseModel):
    """灰度发布创建请求"""
    
    release_name: str
    call_id: str
    target_agent_id: str
    traffic_percentage: int = Field(..., ge=0, le=100)
    config: Optional[Dict[str, Any]] = None


class GrayReleaseUpdateRequest(BaseModel):
    """灰度发布更新请求"""
    
    traffic_percentage: Optional[int] = Field(None, ge=0, le=100)
    status: Optional[Literal["active", "paused", "completed", "rolled_back"]] = None


class GrayReleaseMetricsResponse(BaseModel):
    """灰度发布指标响应"""
    
    release_id: str
    total_requests: int
    target_agent_requests: int
    original_agent_requests: int
    error_rate: float
    avg_latency_ms: float
    rollback_count: int
