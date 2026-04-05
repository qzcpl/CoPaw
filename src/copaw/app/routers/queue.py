# -*- coding: utf-8 -*-
"""Queue management API routes."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/queue", tags=["queue"])


QUEUES_DB: Dict[str, Dict[str, Any]] = {}
QUEUE_MESSAGES: Dict[str, List[Dict[str, Any]]] = {}
DEAD_LETTERS: Dict[str, List[Dict[str, Any]]] = {}


class MessageQueue(BaseModel):
    """Message queue response."""

    queue_id: str
    queue_name: str
    queue_type: Literal["fifo", "standard", "delay"]
    tenant_id: str
    max_size: int
    message_ttl_seconds: int
    visibility_timeout_seconds: int
    status: Literal["active", "paused", "deleted"]
    created_at: str
    updated_at: str


class MessageQueueCreateRequest(BaseModel):
    """Message queue create request."""

    queue_name: str
    queue_type: Literal["fifo", "standard", "delay"] = "standard"
    tenant_id: str
    max_size: Optional[int] = 10000
    message_ttl_seconds: Optional[int] = 86400
    visibility_timeout_seconds: Optional[int] = 30


class MessageQueueUpdateRequest(BaseModel):
    """Message queue update request."""

    queue_name: Optional[str] = None
    max_size: Optional[int] = None
    message_ttl_seconds: Optional[int] = None
    visibility_timeout_seconds: Optional[int] = None
    status: Optional[Literal["active", "paused"]] = None


class QueueMessage(BaseModel):
    """Queue message response."""

    message_id: str
    queue_id: str
    payload: Dict[str, Any]
    status: Literal["pending", "processing", "completed", "failed"]
    retry_count: int
    created_at: str
    processed_at: Optional[str] = None
    error_message: Optional[str] = None


class QueueStatsResponse(BaseModel):
    """Queue stats response."""

    queue_id: str
    current_depth: int
    pending_count: int
    processing_count: int
    completed_count: int
    failed_count: int
    avg_wait_time_ms: float
    avg_processing_time_ms: float


class QueueDepthHistory(BaseModel):
    """Queue depth history response."""

    queue_id: str
    data_points: List[Dict[str, Any]]


class DeadLetterMessage(BaseModel):
    """Dead letter message response."""

    message_id: str
    queue_id: str
    original_message_id: str
    payload: Dict[str, Any]
    error_message: str
    failed_at: str
    retry_count: int


class QueueConsumer(BaseModel):
    """Queue consumer response."""

    consumer_id: str
    queue_id: str
    status: Literal["active", "inactive"]
    last_heartbeat: str
    messages_processed: int


class QueueAlertThreshold(BaseModel):
    """Queue alert threshold response."""

    threshold_id: str
    queue_id: str
    metric_name: str
    threshold_value: float
    comparison_operator: Literal["gt", "lt", "gte", "lte", "eq"]
    severity: Literal["info", "warning", "critical"]
    enabled: bool
    created_at: str


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


@router.get("", response_model=List[MessageQueue])
async def list_message_queues(
    request: Request,
    tenant_id: Optional[str] = Query(None),
    queue_type: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    """List message queues."""
    _get_current_user(request)
    queues = list(QUEUES_DB.values())
    if tenant_id:
        queues = [q for q in queues if q.get("tenant_id") == tenant_id]
    if queue_type:
        queues = [q for q in queues if q.get("queue_type") == queue_type]
    return queues


@router.get("/{queue_id}", response_model=MessageQueue)
async def get_queue(
    request: Request,
    queue_id: str,
) -> Dict[str, Any]:
    """Get queue details."""
    _get_current_user(request)
    queue = QUEUES_DB.get(queue_id)
    if not queue:
        raise HTTPException(
            status_code=404,
            detail=f"Queue not found: {queue_id}",
        )
    return queue


@router.post("", response_model=MessageQueue)
async def create_queue(
    request: Request,
    data: MessageQueueCreateRequest,
) -> Dict[str, Any]:
    """Create queue."""
    _get_current_user(request)
    queue_id = f"queue_{data.queue_name}_{int(datetime.utcnow().timestamp())}"
    queue = {
        "queue_id": queue_id,
        "queue_name": data.queue_name,
        "queue_type": data.queue_type,
        "tenant_id": data.tenant_id,
        "max_size": data.max_size or 10000,
        "message_ttl_seconds": data.message_ttl_seconds or 86400,
        "visibility_timeout_seconds": data.visibility_timeout_seconds or 30,
        "status": "active",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }
    QUEUES_DB[queue_id] = queue
    QUEUE_MESSAGES[queue_id] = []
    DEAD_LETTERS[queue_id] = []
    return queue


@router.put("/{queue_id}", response_model=MessageQueue)
async def update_queue(
    request: Request,
    queue_id: str,
    data: MessageQueueUpdateRequest,
) -> Dict[str, Any]:
    """Update queue."""
    _get_current_user(request)
    queue = QUEUES_DB.get(queue_id)
    if not queue:
        raise HTTPException(
            status_code=404,
            detail=f"Queue not found: {queue_id}",
        )
    if data.queue_name:
        queue["queue_name"] = data.queue_name
    if data.max_size:
        queue["max_size"] = data.max_size
    if data.message_ttl_seconds:
        queue["message_ttl_seconds"] = data.message_ttl_seconds
    if data.visibility_timeout_seconds:
        queue["visibility_timeout_seconds"] = data.visibility_timeout_seconds
    if data.status:
        queue["status"] = data.status
    queue["updated_at"] = datetime.utcnow().isoformat() + "Z"
    return queue


@router.delete("/{queue_id}")
async def delete_queue(
    request: Request,
    queue_id: str,
) -> Dict[str, str]:
    """Delete queue."""
    _get_current_user(request)
    if queue_id not in QUEUES_DB:
        raise HTTPException(
            status_code=404,
            detail=f"Queue not found: {queue_id}",
        )
    del QUEUES_DB[queue_id]
    QUEUE_MESSAGES.pop(queue_id, None)
    DEAD_LETTERS.pop(queue_id, None)
    return {"message": "Queue deleted successfully"}


@router.get("/{queue_id}/status", response_model=MessageQueue)
async def get_queue_status(
    request: Request,
    queue_id: str,
) -> Dict[str, Any]:
    """Get queue status."""
    return await get_queue(request, queue_id)


@router.get("/{queue_id}/stats", response_model=QueueStatsResponse)
async def get_queue_stats(
    request: Request,
    queue_id: str,
) -> Dict[str, Any]:
    """Get queue stats."""
    _get_current_user(request)
    messages = QUEUE_MESSAGES.get(queue_id, [])
    return {
        "queue_id": queue_id,
        "current_depth": len(messages),
        "pending_count": len(
            [m for m in messages if m.get("status") == "pending"],
        ),
        "processing_count": len(
            [m for m in messages if m.get("status") == "processing"],
        ),
        "completed_count": len(
            [m for m in messages if m.get("status") == "completed"],
        ),
        "failed_count": len(
            [m for m in messages if m.get("status") == "failed"],
        ),
        "avg_wait_time_ms": 0.0,
        "avg_processing_time_ms": 0.0,
    }


@router.get("/{queue_id}/depth/history", response_model=QueueDepthHistory)
async def get_queue_depth_history(
    request: Request,
    queue_id: str,
    start_time: str = Query(...),
    end_time: str = Query(...),
    aggregation_interval_sec: int = Query(60),
) -> Dict[str, Any]:
    """Get queue depth history."""
    _get_current_user(request)
    return {
        "queue_id": queue_id,
        "data_points": [],
    }


@router.get("/{queue_id}/messages", response_model=List[QueueMessage])
async def list_queue_messages(
    request: Request,
    queue_id: str,
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
) -> List[Dict[str, Any]]:
    """List queue messages."""
    _get_current_user(request)
    messages = QUEUE_MESSAGES.get(queue_id, [])
    if status:
        messages = [m for m in messages if m.get("status") == status]
    return messages[:limit]


@router.get("/{queue_id}/messages/{message_id}", response_model=QueueMessage)
async def get_queue_message(
    request: Request,
    queue_id: str,
    message_id: str,
) -> Dict[str, Any]:
    """Get queue message details."""
    _get_current_user(request)
    messages = QUEUE_MESSAGES.get(queue_id, [])
    for msg in messages:
        if msg.get("message_id") == message_id:
            return msg
    raise HTTPException(
        status_code=404,
        detail=f"Message not found: {message_id}",
    )


@router.get("/{queue_id}/dead-letter", response_model=List[DeadLetterMessage])
async def list_dead_letter_messages(
    request: Request,
    queue_id: str,
    limit: int = Query(50, ge=1, le=100),
) -> List[Dict[str, Any]]:
    """List dead letter messages."""
    _get_current_user(request)
    messages = DEAD_LETTERS.get(queue_id, [])
    return messages[:limit]


@router.post("/{queue_id}/dead-letter/{message_id}/reprocess")
async def reprocess_dead_letter_message(
    request: Request,
    queue_id: str,
    message_id: str,
) -> Dict[str, str]:
    """Reprocess dead letter message."""
    _get_current_user(request)
    return {"message": "Message reprocessed successfully"}


@router.delete("/{queue_id}/dead-letter/{message_id}")
async def delete_dead_letter_message(
    request: Request,
    queue_id: str,
    message_id: str,
) -> Dict[str, str]:
    """Delete dead letter message."""
    _get_current_user(request)
    messages = DEAD_LETTERS.get(queue_id, [])
    DEAD_LETTERS[queue_id] = [
        m for m in messages if m.get("message_id") != message_id
    ]
    return {"message": "Dead letter message deleted successfully"}


@router.get("/{queue_id}/consumers", response_model=List[QueueConsumer])
async def list_queue_consumers(
    request: Request,
    queue_id: str,
) -> List[Dict[str, Any]]:
    """List queue consumers."""
    _get_current_user(request)
    return []


@router.post("/{queue_id}/pause")
async def pause_queue(
    request: Request,
    queue_id: str,
) -> Dict[str, str]:
    """Pause queue."""
    _get_current_user(request)
    queue = QUEUES_DB.get(queue_id)
    if not queue:
        raise HTTPException(
            status_code=404,
            detail=f"Queue not found: {queue_id}",
        )
    queue["status"] = "paused"
    return {"message": "Queue paused successfully"}


@router.post("/{queue_id}/resume")
async def resume_queue(
    request: Request,
    queue_id: str,
) -> Dict[str, str]:
    """Resume queue."""
    _get_current_user(request)
    queue = QUEUES_DB.get(queue_id)
    if not queue:
        raise HTTPException(
            status_code=404,
            detail=f"Queue not found: {queue_id}",
        )
    queue["status"] = "active"
    return {"message": "Queue resumed successfully"}


@router.post("/{queue_id}/purge")
async def purge_queue(
    request: Request,
    queue_id: str,
    status: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Purge queue."""
    _get_current_user(request)
    if queue_id not in QUEUES_DB:
        raise HTTPException(
            status_code=404,
            detail=f"Queue not found: {queue_id}",
        )
    messages = QUEUE_MESSAGES.get(queue_id, [])
    if status:
        QUEUE_MESSAGES[queue_id] = [
            m for m in messages if m.get("status") != status
        ]
        purged_count = len([m for m in messages if m.get("status") == status])
    else:
        QUEUE_MESSAGES[queue_id] = []
        purged_count = len(messages)
    return {
        "message": "Queue purged successfully",
        "purged_count": purged_count,
    }


@router.get(
    "/{queue_id}/alerts/thresholds",
    response_model=List[QueueAlertThreshold],
)
async def list_queue_alert_thresholds(
    request: Request,
    queue_id: str,
) -> List[Dict[str, Any]]:
    """List queue alert thresholds."""
    _get_current_user(request)
    return []


@router.post(
    "/{queue_id}/alerts/thresholds",
    response_model=QueueAlertThreshold,
)
async def create_queue_alert_threshold(
    request: Request,
    queue_id: str,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """Create queue alert threshold."""
    _get_current_user(request)
    if queue_id not in QUEUES_DB:
        raise HTTPException(
            status_code=404,
            detail=f"Queue not found: {queue_id}",
        )
    threshold_id = f"threshold_{int(datetime.utcnow().timestamp())}"
    return {
        "threshold_id": threshold_id,
        "queue_id": queue_id,
        "metric_name": data.get("metric_name", "depth"),
        "threshold_value": data.get("threshold_value", 100),
        "comparison_operator": data.get("comparison_operator", "gt"),
        "severity": data.get("severity", "warning"),
        "enabled": True,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }


@router.put(
    "/{queue_id}/alerts/thresholds/{threshold_id}",
    response_model=QueueAlertThreshold,
)
async def update_queue_alert_threshold(
    request: Request,
    queue_id: str,
    threshold_id: str,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """Update queue alert threshold."""
    _get_current_user(request)
    if queue_id not in QUEUES_DB:
        raise HTTPException(
            status_code=404,
            detail=f"Queue not found: {queue_id}",
        )
    return {
        "threshold_id": threshold_id,
        "queue_id": queue_id,
        "metric_name": data.get("metric_name", "depth"),
        "threshold_value": data.get("threshold_value", 100),
        "comparison_operator": data.get("comparison_operator", "gt"),
        "severity": data.get("severity", "warning"),
        "enabled": data.get("enabled", True),
        "created_at": datetime.utcnow().isoformat() + "Z",
    }


@router.delete("/{queue_id}/alerts/thresholds/{threshold_id}")
async def delete_queue_alert_threshold(
    request: Request,
    queue_id: str,
    threshold_id: str,
) -> Dict[str, str]:
    """Delete queue alert threshold."""
    _get_current_user(request)
    if queue_id not in QUEUES_DB:
        raise HTTPException(
            status_code=404,
            detail=f"Queue not found: {queue_id}",
        )
    return {"message": "Alert threshold deleted successfully"}
