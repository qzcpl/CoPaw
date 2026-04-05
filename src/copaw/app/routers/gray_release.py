# -*- coding: utf-8 -*-
"""Gray release API routes."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/gray-release", tags=["gray_release"])


GRAY_RELEASES_DB: Dict[str, Dict[str, Any]] = {}


class GrayReleaseConfig(BaseModel):
    """Gray release config response."""

    config_id: str
    config_name: str
    tenant_id: str
    target_type: Literal["agent", "channel", "callid", "skill"]
    target_id: str
    gray_strategy: Literal["percentage", "whitelist", "canary", "ab_test"]
    gray_percentage: int = Field(..., ge=0, le=100)
    whitelist: Optional[List[str]] = None
    status: Literal[
        "draft",
        "pending",
        "running",
        "paused",
        "completed",
        "rolled_back",
    ] = "draft"
    description: Optional[str] = None
    start_at: Optional[str] = None
    end_at: Optional[str] = None
    created_at: str
    updated_at: str


class GrayReleaseCreateRequest(BaseModel):
    """Gray release create request."""

    config_name: str
    tenant_id: str
    target_type: Literal["agent", "channel", "callid", "skill"]
    target_id: str
    gray_strategy: Literal["percentage", "whitelist", "canary", "ab_test"]
    gray_percentage: int = Field(default=0, ge=0, le=100)
    whitelist: Optional[List[str]] = None
    description: Optional[str] = None


class GrayReleaseUpdateRequest(BaseModel):
    """Gray release update request."""

    config_name: Optional[str] = None
    gray_strategy: Optional[
        Literal["percentage", "whitelist", "canary", "ab_test"]
    ] = None
    gray_percentage: Optional[int] = Field(default=None, ge=0, le=100)
    whitelist: Optional[List[str]] = None
    status: Optional[
        Literal[
            "draft",
            "pending",
            "running",
            "paused",
            "completed",
            "rolled_back",
        ]
    ] = None
    description: Optional[str] = None


class GrayReleaseStats(BaseModel):
    """Gray release stats response."""

    config_id: str
    total_requests: int
    gray_requests: int
    gray_percentage: float
    success_rate: float
    avg_latency_ms: float
    error_count: int
    stats_at: str


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


@router.get("", response_model=List[GrayReleaseConfig])
async def list_gray_releases(
    request: Request,
    tenant_id: Optional[str] = Query(None),
    target_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    """List gray release configs."""
    _get_current_user(request)
    releases = list(GRAY_RELEASES_DB.values())
    if tenant_id:
        releases = [r for r in releases if r.get("tenant_id") == tenant_id]
    if target_type:
        releases = [r for r in releases if r.get("target_type") == target_type]
    if status:
        releases = [r for r in releases if r.get("status") == status]
    return releases


@router.get("/{config_id}", response_model=GrayReleaseConfig)
async def get_gray_release(
    request: Request,
    config_id: str,
) -> Dict[str, Any]:
    """Get gray release config details."""
    _get_current_user(request)
    config = GRAY_RELEASES_DB.get(config_id)
    if not config:
        raise HTTPException(
            status_code=404,
            detail=f"Gray release not found: {config_id}",
        )
    return config


@router.post("", response_model=GrayReleaseConfig)
async def create_gray_release(
    request: Request,
    data: GrayReleaseCreateRequest,
) -> Dict[str, Any]:
    """Create gray release config."""
    _get_current_user(request)
    config_id = f"gray_{data.config_name}_{int(datetime.utcnow().timestamp())}"
    config = {
        "config_id": config_id,
        "config_name": data.config_name,
        "tenant_id": data.tenant_id,
        "target_type": data.target_type,
        "target_id": data.target_id,
        "gray_strategy": data.gray_strategy,
        "gray_percentage": data.gray_percentage,
        "whitelist": data.whitelist or [],
        "status": "draft",
        "description": data.description,
        "start_at": None,
        "end_at": None,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }
    GRAY_RELEASES_DB[config_id] = config
    return config


@router.put("/{config_id}", response_model=GrayReleaseConfig)
async def update_gray_release(
    request: Request,
    config_id: str,
    data: GrayReleaseUpdateRequest,
) -> Dict[str, Any]:
    """Update gray release config."""
    _get_current_user(request)
    config = GRAY_RELEASES_DB.get(config_id)
    if not config:
        raise HTTPException(
            status_code=404,
            detail=f"Gray release not found: {config_id}",
        )
    if data.config_name:
        config["config_name"] = data.config_name
    if data.gray_strategy:
        config["gray_strategy"] = data.gray_strategy
    if data.gray_percentage is not None:
        config["gray_percentage"] = data.gray_percentage
    if data.whitelist is not None:
        config["whitelist"] = data.whitelist
    if data.status:
        config["status"] = data.status
    if data.description is not None:
        config["description"] = data.description
    config["updated_at"] = datetime.utcnow().isoformat() + "Z"
    return config


@router.delete("/{config_id}")
async def delete_gray_release(
    request: Request,
    config_id: str,
) -> Dict[str, str]:
    """Delete gray release config."""
    _get_current_user(request)
    if config_id not in GRAY_RELEASES_DB:
        raise HTTPException(
            status_code=404,
            detail=f"Gray release not found: {config_id}",
        )
    del GRAY_RELEASES_DB[config_id]
    return {"message": "Gray release deleted successfully"}


@router.post("/{config_id}/start")
async def start_gray_release(
    request: Request,
    config_id: str,
) -> Dict[str, Any]:
    """Start gray release."""
    _get_current_user(request)
    config = GRAY_RELEASES_DB.get(config_id)
    if not config:
        raise HTTPException(
            status_code=404,
            detail=f"Gray release not found: {config_id}",
        )
    config["status"] = "running"
    config["start_at"] = datetime.utcnow().isoformat() + "Z"
    config["updated_at"] = datetime.utcnow().isoformat() + "Z"
    return config


@router.post("/{config_id}/pause")
async def pause_gray_release(
    request: Request,
    config_id: str,
) -> Dict[str, str]:
    """Pause gray release."""
    _get_current_user(request)
    config = GRAY_RELEASES_DB.get(config_id)
    if not config:
        raise HTTPException(
            status_code=404,
            detail=f"Gray release not found: {config_id}",
        )
    config["status"] = "paused"
    config["updated_at"] = datetime.utcnow().isoformat() + "Z"
    return {"message": "Gray release paused successfully"}


@router.post("/{config_id}/resume")
async def resume_gray_release(
    request: Request,
    config_id: str,
) -> Dict[str, str]:
    """Resume gray release."""
    _get_current_user(request)
    config = GRAY_RELEASES_DB.get(config_id)
    if not config:
        raise HTTPException(
            status_code=404,
            detail=f"Gray release not found: {config_id}",
        )
    config["status"] = "running"
    config["updated_at"] = datetime.utcnow().isoformat() + "Z"
    return {"message": "Gray release resumed successfully"}


@router.post("/{config_id}/stop")
async def stop_gray_release(
    request: Request,
    config_id: str,
) -> Dict[str, str]:
    """Stop gray release."""
    _get_current_user(request)
    config = GRAY_RELEASES_DB.get(config_id)
    if not config:
        raise HTTPException(
            status_code=404,
            detail=f"Gray release not found: {config_id}",
        )
    config["status"] = "completed"
    config["end_at"] = datetime.utcnow().isoformat() + "Z"
    config["updated_at"] = datetime.utcnow().isoformat() + "Z"
    return {"message": "Gray release stopped successfully"}


@router.post("/{config_id}/rollback")
async def rollback_gray_release(
    request: Request,
    config_id: str,
    data: Dict[str, Any],
) -> Dict[str, str]:
    """Rollback gray release."""
    _get_current_user(request)
    config = GRAY_RELEASES_DB.get(config_id)
    if not config:
        raise HTTPException(
            status_code=404,
            detail=f"Gray release not found: {config_id}",
        )
    config["status"] = "rolled_back"
    config["end_at"] = datetime.utcnow().isoformat() + "Z"
    config["updated_at"] = datetime.utcnow().isoformat() + "Z"
    return {"message": "Gray release rolled back successfully"}


@router.get("/{config_id}/stats", response_model=GrayReleaseStats)
async def get_gray_release_stats(
    request: Request,
    config_id: str,
    start_time: str = Query(...),
    end_time: str = Query(...),
) -> Dict[str, Any]:
    """Get gray release stats."""
    _get_current_user(request)
    if config_id not in GRAY_RELEASES_DB:
        raise HTTPException(
            status_code=404,
            detail=f"Gray release not found: {config_id}",
        )
    return {
        "config_id": config_id,
        "total_requests": 0,
        "gray_requests": 0,
        "gray_percentage": 0.0,
        "success_rate": 100.0,
        "avg_latency_ms": 0.0,
        "error_count": 0,
        "stats_at": datetime.utcnow().isoformat() + "Z",
    }
