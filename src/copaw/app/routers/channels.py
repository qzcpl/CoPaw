# -*- coding: utf-8 -*-
"""Channel management API routes - delegates to agent.config.channels."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Path, Query, Request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/channels", tags=["channels"])


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


@router.get("")
async def list_channels(request: Request) -> List[Dict[str, Any]]:
    """List all channels - delegates to agent.config.channels."""
    from datetime import datetime
    from ..agent_context import get_agent_for_request

    _get_current_user(request)
    agent = await get_agent_for_request(request)
    agent_config = agent.config

    channels = agent_config.channels
    if channels is None:
        return []

    all_configs = channels.model_dump()
    extra = getattr(channels, "__pydantic_extra__", None) or {}
    all_configs.update(extra)

    result = []
    for key, value in all_configs.items():
        if isinstance(value, dict):
            config_dict = value
        else:
            config_dict = (
                value.model_dump() if hasattr(value, "model_dump") else {}
            )

        channel_data = {
            "channel_id": key,
            "channel_name": key.capitalize(),
            "platform": key,
            "status": (
                "active" if config_dict.get("enabled", False) else "inactive"
            ),
            "config": config_dict,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
            "tenant_id": "default",
        }
        result.append(channel_data)

    return result


@router.get("/{channel_id}")
async def get_channel(
    request: Request,
    channel_id: str,
) -> Dict[str, Any]:
    """Get channel details - delegates to agent.config.channels."""
    from datetime import datetime
    from ..agent_context import get_agent_for_request

    _get_current_user(request)
    agent = await get_agent_for_request(request)
    channels = agent.config.channels

    if channels is None:
        raise HTTPException(
            status_code=404,
            detail=f"Channel not found: {channel_id}",
        )

    all_configs = channels.model_dump()
    extra = getattr(channels, "__pydantic_extra__", None) or {}
    all_configs.update(extra)

    if channel_id not in all_configs:
        raise HTTPException(
            status_code=404,
            detail=f"Channel not found: {channel_id}",
        )

    value = all_configs[channel_id]
    if isinstance(value, dict):
        config_dict = value
    else:
        config_dict = (
            value.model_dump() if hasattr(value, "model_dump") else {}
        )

    return {
        "channel_id": channel_id,
        "channel_name": channel_id.capitalize(),
        "platform": channel_id,
        "status": (
            "active" if config_dict.get("enabled", False) else "inactive"
        ),
        "config": config_dict,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "tenant_id": "default",
    }


@router.post("")
async def create_channel(
    request: Request,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """Create channel - not supported via this API."""
    raise HTTPException(
        status_code=501,
        detail="Channel creation not supported. Use /config/channels to update channel configuration.",
    )


@router.put("/{channel_id}")
async def update_channel(
    request: Request,
    channel_id: str,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """Update channel - delegates to agent.config.channels."""
    from ...config.config import save_agent_config

    _get_current_user(request)
    agent = await get_agent_for_request(request)

    if agent.config.channels is None:
        agent.config.channels = {}

    setattr(agent.config.channels, channel_id, data)
    save_agent_config(agent.agent_id, agent.config)

    return {
        "channel_id": channel_id,
        "channel_name": channel_id,
        "platform": channel_id,
        **data,
    }


@router.delete("/{channel_id}")
async def delete_channel(
    request: Request,
    channel_id: str,
) -> Dict[str, str]:
    """Delete channel - not supported via this API."""
    raise HTTPException(
        status_code=501,
        detail="Channel deletion not supported via this API.",
    )


@router.get("/{channel_id}/instances")
async def list_channel_instances(
    request: Request,
    channel_id: str,
) -> List[Dict[str, Any]]:
    """List channel instances - returns empty for now."""
    _get_current_user(request)
    return []


@router.get("/{channel_id}/instances/{instance_id}")
async def get_channel_instance(
    request: Request,
    channel_id: str,
    instance_id: str,
) -> Dict[str, Any]:
    """Get channel instance - not implemented."""
    raise HTTPException(
        status_code=501,
        detail="Channel instances not implemented.",
    )


@router.post("/{channel_id}/instances")
async def create_channel_instance(
    request: Request,
    channel_id: str,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """Create channel instance - not implemented."""
    raise HTTPException(
        status_code=501,
        detail="Channel instances not implemented.",
    )


@router.put("/{channel_id}/instances/{instance_id}")
async def update_channel_instance(
    request: Request,
    channel_id: str,
    instance_id: str,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """Update channel instance - not implemented."""
    raise HTTPException(
        status_code=501,
        detail="Channel instances not implemented.",
    )


@router.post("/{channel_id}/instances/{instance_id}/connect")
async def connect_channel_instance(
    request: Request,
    channel_id: str,
    instance_id: str,
) -> Dict[str, str]:
    """Connect channel instance - not implemented."""
    raise HTTPException(
        status_code=501,
        detail="Channel instances not implemented.",
    )


@router.post("/{channel_id}/instances/{instance_id}/disconnect")
async def disconnect_channel_instance(
    request: Request,
    channel_id: str,
    instance_id: str,
) -> Dict[str, str]:
    """Disconnect channel instance - not implemented."""
    raise HTTPException(
        status_code=501,
        detail="Channel instances not implemented.",
    )


@router.post("/{channel_id}/instances/{instance_id}/restart")
async def restart_channel_instance(
    request: Request,
    channel_id: str,
    instance_id: str,
) -> Dict[str, str]:
    """Restart channel instance - not implemented."""
    raise HTTPException(
        status_code=501,
        detail="Channel instances not implemented.",
    )


@router.get("/{channel_id}/stats")
async def get_channel_stats(
    request: Request,
    channel_id: str,
) -> Dict[str, Any]:
    """Get channel stats - returns empty stats."""
    _get_current_user(request)
    return {
        "channel_id": channel_id,
        "total_messages": 0,
        "messages_today": 0,
        "active_instances": 0,
        "error_count": 0,
        "avg_response_time_ms": 0.0,
    }


@router.get("/{channel_id}/health")
async def get_channel_health(
    request: Request,
    channel_id: str,
) -> Dict[str, Any]:
    """Get channel health status - returns healthy."""
    _get_current_user(request)
    return {
        "channel_id": channel_id,
        "status": "healthy",
        "uptime_seconds": 0.0,
        "last_check": "",
        "checks_passed": 0,
        "checks_failed": 0,
    }
