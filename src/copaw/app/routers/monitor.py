# -*- coding: utf-8 -*-
"""Monitor API routes."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitor", tags=["monitor"])


METRICS_DB: Dict[str, Dict[str, Any]] = {}
ALERTS_DB: Dict[str, Dict[str, Any]] = {}
ALERT_HISTORY: List[Dict[str, Any]] = []


class MonitorMetric(BaseModel):
    """Monitor metric response."""

    metric_id: str
    metric_name: str
    metric_type: Literal["gauge", "counter", "histogram"]
    value: float
    unit: str
    timestamp: str
    labels: Optional[Dict[str, str]] = None


class MonitorAlert(BaseModel):
    """Monitor alert response."""

    alert_id: str
    alert_name: str
    metric_id: str
    threshold: float
    operator: Literal["gt", "lt", "gte", "lte", "eq"]
    severity: Literal["INFO", "WARNING", "ERROR", "CRITICAL"]
    status: Literal["active", "resolved", "muted"]
    channels: List[str]
    created_at: str
    triggered_at: Optional[str] = None
    resolved_at: Optional[str] = None


class AlertCreateRequest(BaseModel):
    """Alert create request."""

    alert_name: str
    metric_id: str
    threshold: float
    operator: Literal["gt", "lt", "gte", "lte", "eq"]
    severity: Literal["INFO", "WARNING", "ERROR", "CRITICAL"]
    channels: List[str]


class AlertUpdateRequest(BaseModel):
    """Alert update request."""

    alert_name: Optional[str] = None
    threshold: Optional[float] = None
    operator: Optional[Literal["gt", "lt", "gte", "lte", "eq"]] = None
    severity: Optional[Literal["INFO", "WARNING", "ERROR", "CRITICAL"]] = None
    channels: Optional[List[str]] = None
    status: Optional[Literal["active", "resolved", "muted"]] = None


def _get_current_user(request: Request) -> Dict[str, str]:
    """Get current user from request state."""
    user = getattr(request.state, "user", None)
    if not user:
        return {
            "user_id": "default",
            "tenant_id": "default",
            "role": "tenant_admin",
        }
    return {
        "user_id": user,
        "tenant_id": "default",
        "role": "tenant_admin",
    }


@router.get("/metrics", response_model=List[MonitorMetric])
async def get_metrics(
    request: Request,
    tenant_id: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    """Get system metrics."""
    _get_current_user(request)
    return list(METRICS_DB.values())


@router.get("/metrics/{metric_id}", response_model=MonitorMetric)
async def get_metric(
    request: Request,
    metric_id: str,
) -> Dict[str, Any]:
    """Get metric details."""
    _get_current_user(request)
    metric = METRICS_DB.get(metric_id)
    if not metric:
        raise HTTPException(
            status_code=404,
            detail=f"Metric not found: {metric_id}",
        )
    return metric


@router.get("/alerts", response_model=List[MonitorAlert])
async def list_alerts(
    request: Request,
    tenant_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    """List alerts."""
    _get_current_user(request)
    alerts = list(ALERTS_DB.values())
    if status:
        alerts = [a for a in alerts if a.get("status") == status]
    return alerts


@router.get("/alerts/{alert_id}", response_model=MonitorAlert)
async def get_alert(
    request: Request,
    alert_id: str,
) -> Dict[str, Any]:
    """Get alert details."""
    _get_current_user(request)
    alert = ALERTS_DB.get(alert_id)
    if not alert:
        raise HTTPException(
            status_code=404,
            detail=f"Alert not found: {alert_id}",
        )
    return alert


@router.post("/alerts", response_model=MonitorAlert)
async def create_alert(
    request: Request,
    data: AlertCreateRequest,
) -> Dict[str, Any]:
    """Create alert."""
    _get_current_user(request)
    alert_id = f"alert_{data.alert_name}_{int(datetime.utcnow().timestamp())}"
    alert = {
        "alert_id": alert_id,
        "alert_name": data.alert_name,
        "metric_id": data.metric_id,
        "threshold": data.threshold,
        "operator": data.operator,
        "severity": data.severity,
        "status": "active",
        "channels": data.channels,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "triggered_at": None,
        "resolved_at": None,
    }
    ALERTS_DB[alert_id] = alert
    return alert


@router.put("/alerts/{alert_id}", response_model=MonitorAlert)
async def update_alert(
    request: Request,
    alert_id: str,
    data: AlertUpdateRequest,
) -> Dict[str, Any]:
    """Update alert."""
    _get_current_user(request)
    alert = ALERTS_DB.get(alert_id)
    if not alert:
        raise HTTPException(
            status_code=404,
            detail=f"Alert not found: {alert_id}",
        )
    if data.alert_name:
        alert["alert_name"] = data.alert_name
    if data.threshold is not None:
        alert["threshold"] = data.threshold
    if data.operator:
        alert["operator"] = data.operator
    if data.severity:
        alert["severity"] = data.severity
    if data.channels:
        alert["channels"] = data.channels
    if data.status:
        alert["status"] = data.status
        if data.status == "resolved":
            alert["resolved_at"] = datetime.utcnow().isoformat() + "Z"
    return alert


@router.delete("/alerts/{alert_id}")
async def delete_alert(
    request: Request,
    alert_id: str,
) -> Dict[str, str]:
    """Delete alert."""
    _get_current_user(request)
    if alert_id not in ALERTS_DB:
        raise HTTPException(
            status_code=404,
            detail=f"Alert not found: {alert_id}",
        )
    del ALERTS_DB[alert_id]
    return {"message": "Alert deleted successfully"}
