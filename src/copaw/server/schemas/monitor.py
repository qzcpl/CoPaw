"""
监控相关 Schema
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime


class MetricResponse(BaseModel):
    """指标响应"""
    
    metric_id: str
    metric_name: str
    metric_type: Literal["counter", "gauge", "histogram"]
    value: float
    unit: str
    labels: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime


class MetricQueryRequest(BaseModel):
    """指标查询请求"""
    
    metric_name: str
    start_time: datetime
    end_time: datetime
    labels: Optional[Dict[str, str]] = None
    aggregation: Optional[Literal["avg", "sum", "max", "min"]] = "avg"


class MetricQueryResponse(BaseModel):
    """指标查询响应"""
    
    metric_name: str
    data_points: List[Dict[str, Any]]
    start_time: datetime
    end_time: datetime


class AlertResponse(BaseModel):
    """告警响应"""
    
    alert_id: str
    alert_name: str
    metric_name: str
    condition: str
    threshold: float
    severity: Literal["INFO", "WARNING", "ERROR", "CRITICAL"]
    status: Literal["active", "resolved", "silenced"]
    channels: List[Literal["LOG", "EMAIL", "DINGTALK", "WEBHOOK"]]
    created_at: datetime
    updated_at: datetime


class AlertCreateRequest(BaseModel):
    """告警创建请求"""
    
    alert_name: str
    metric_name: str
    condition: Literal["gt", "lt", "eq", "gte", "lte"]
    threshold: float
    severity: Literal["INFO", "WARNING", "ERROR", "CRITICAL"]
    channels: List[Literal["LOG", "EMAIL", "DINGTALK", "WEBHOOK"]]


class AlertUpdateRequest(BaseModel):
    """告警更新请求"""
    
    alert_name: Optional[str] = None
    threshold: Optional[float] = None
    severity: Optional[Literal["INFO", "WARNING", "ERROR", "CRITICAL"]] = None
    channels: Optional[List[Literal["LOG", "EMAIL", "DINGTALK", "WEBHOOK"]]] = None
    status: Optional[Literal["active", "resolved", "silenced"]] = None


class AlertHistoryResponse(BaseModel):
    """告警历史响应"""
    
    alert_id: str
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    triggered_value: float
    severity: Literal["INFO", "WARNING", "ERROR", "CRITICAL"]
    message: str
