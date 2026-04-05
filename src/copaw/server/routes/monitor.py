"""
监控 API
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime

from ..schemas.monitor import (
    MetricResponse,
    MetricQueryRequest,
    MetricQueryResponse,
    AlertResponse,
    AlertCreateRequest,
    AlertUpdateRequest,
    AlertHistoryResponse,
)
from ..core.exceptions import ApiError, ApiErrorCode
from ..dependencies import get_current_user

router = APIRouter()

# 模拟指标和告警数据库
METRICS_DB = {}
ALERTS_DB = {}
ALERT_HISTORY = []


@router.get("/metrics", response_model=List[MetricResponse])
async def list_metrics(
    tenant_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    列出监控指标
    
    Args:
        tenant_id: 租户 ID
        current_user: 当前用户
    
    Returns:
        指标列表
    """
    return list(METRICS_DB.values())


@router.post("/metrics/query", response_model=MetricQueryResponse)
async def query_metrics(
    request: MetricQueryRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    查询指标
    
    Args:
        request: 查询请求
        current_user: 当前用户
    
    Returns:
        指标数据
    """
    # TODO: 实现真实指标查询
    return MetricQueryResponse(
        metric_name=request.metric_name,
        data_points=[],
        start_time=request.start_time,
        end_time=request.end_time,
    )


@router.get("/alerts", response_model=List[AlertResponse])
async def list_alerts(
    tenant_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    列出告警
    
    Args:
        tenant_id: 租户 ID
        status: 告警状态
        current_user: 当前用户
    
    Returns:
        告警列表
    """
    alerts = list(ALERTS_DB.values())
    
    # 过滤
    if status:
        alerts = [a for a in alerts if a["status"] == status]
    
    return alerts


@router.post("/alerts", response_model=AlertResponse)
async def create_alert(
    request: AlertCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    创建告警
    
    Args:
        request: 创建请求
        current_user: 当前用户
    
    Returns:
        创建的告警
    """
    # 权限检查
    if current_user["role"] not in ["tenant_admin", "system_admin"]:
        raise ApiError(
            code=ApiErrorCode.PERMISSION_DENIED,
            message="Only tenant admin can create alert",
            status_code=403,
        )
    
    alert_id = f"alert_{request.alert_name}_{int(datetime.utcnow().timestamp())}"
    
    alert = {
        "alert_id": alert_id,
        "alert_name": request.alert_name,
        "metric_name": request.metric_name,
        "condition": request.condition,
        "threshold": request.threshold,
        "severity": request.severity,
        "status": "active",
        "channels": request.channels,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }
    
    ALERTS_DB[alert_id] = alert
    
    return alert


@router.put("/alerts/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: str,
    request: AlertUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    更新告警
    
    Args:
        alert_id: 告警 ID
        request: 更新请求
        current_user: 当前用户
    
    Returns:
        更新后的告警
    """
    alert = ALERTS_DB.get(alert_id)
    
    if not alert:
        raise ApiError(
            code=ApiErrorCode.ALERT_NOT_FOUND,
            message=f"Alert not found: {alert_id}",
            status_code=404,
        )
    
    # 更新字段
    if request.alert_name:
        alert["alert_name"] = request.alert_name
    if request.threshold:
        alert["threshold"] = request.threshold
    if request.severity:
        alert["severity"] = request.severity
    if request.channels:
        alert["channels"] = request.channels
    if request.status:
        alert["status"] = request.status
    alert["updated_at"] = datetime.utcnow().isoformat() + "Z"
    
    return alert


@router.delete("/alerts/{alert_id}")
async def delete_alert(
    alert_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    删除告警
    
    Args:
        alert_id: 告警 ID
        current_user: 当前用户
    """
    alert = ALERTS_DB.get(alert_id)
    
    if not alert:
        raise ApiError(
            code=ApiErrorCode.ALERT_NOT_FOUND,
            message=f"Alert not found: {alert_id}",
            status_code=404,
        )
    
    # 权限检查
    if current_user["role"] not in ["tenant_admin", "system_admin"]:
        raise ApiError(
            code=ApiErrorCode.PERMISSION_DENIED,
            message="Only tenant admin can delete alert",
            status_code=403,
        )
    
    del ALERTS_DB[alert_id]
    
    return {"message": "Alert deleted successfully"}


@router.get("/alerts/{alert_id}/history", response_model=List[AlertHistoryResponse])
async def get_alert_history(
    alert_id: str,
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    """
    查询告警历史
    
    Args:
        alert_id: 告警 ID
        limit: 返回记录数
        current_user: 当前用户
    
    Returns:
        告警历史
    """
    # 过滤
    history = [h for h in ALERT_HISTORY if h["alert_id"] == alert_id]
    
    # 按时间倒序，限制数量
    history = sorted(history, key=lambda x: x["triggered_at"], reverse=True)[:limit]
    
    return history
