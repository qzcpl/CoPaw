# -*- coding: utf-8 -*-
"""Bot management API routes."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bots", tags=["bots"])


BOTS_DB: Dict[str, Dict[str, Any]] = {}


class BotInfo(BaseModel):
    """Bot info response."""

    bot_id: str
    bot_name: str
    tenant_id: str
    platform: Literal[
        "dingtalk",
        "feishu",
        "wecom",
        "wechat",
        "telegram",
        "discord",
    ]
    config: Dict[str, Any]
    status: Literal["connected", "disconnected", "pending"]
    created_at: str
    updated_at: str
    connected_at: Optional[str] = None
    webhook_url: Optional[str] = None
    client_id: Optional[str] = None


class BotCreateRequest(BaseModel):
    """Bot create request."""

    bot_name: str
    tenant_id: str
    platform: Literal[
        "dingtalk",
        "feishu",
        "wecom",
        "wechat",
        "telegram",
        "discord",
    ]
    config: Optional[Dict[str, Any]] = None
    webhook_url: Optional[str] = None


class BotUpdateRequest(BaseModel):
    """Bot update request."""

    bot_name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    status: Optional[Literal["connected", "disconnected", "pending"]] = None


class BotConnectRequest(BaseModel):
    """Bot connect request."""

    bot_id: str
    client_id: str
    webhook_url: str


class BotStatusResponse(BaseModel):
    """Bot status response."""

    bot_id: str
    status: Literal["connected", "disconnected", "pending"]
    last_heartbeat: Optional[datetime] = None
    message_count: int = 0
    error_count: int = 0


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


@router.get("", response_model=List[BotInfo])
async def list_bots(
    request: Request,
    tenant_id: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    """List bots."""
    _get_current_user(request)
    bots = list(BOTS_DB.values())
    if tenant_id:
        bots = [b for b in bots if b.get("tenant_id") == tenant_id]
    if platform:
        bots = [b for b in bots if b.get("platform") == platform]
    return bots


@router.get("/{bot_id}", response_model=BotInfo)
async def get_bot(
    request: Request,
    bot_id: str,
) -> Dict[str, Any]:
    """Get bot details."""
    _get_current_user(request)
    bot = BOTS_DB.get(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail=f"Bot not found: {bot_id}")
    return bot


@router.post("", response_model=BotInfo)
async def create_bot(
    request: Request,
    data: BotCreateRequest,
) -> Dict[str, Any]:
    """Create bot."""
    _get_current_user(request)
    bot_id = f"bot_{data.bot_name}_{int(datetime.utcnow().timestamp())}"
    bot = {
        "bot_id": bot_id,
        "bot_name": data.bot_name,
        "tenant_id": data.tenant_id,
        "platform": data.platform,
        "config": data.config or {},
        "status": "pending",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "connected_at": None,
        "webhook_url": data.webhook_url,
        "client_id": None,
    }
    BOTS_DB[bot_id] = bot
    return bot


@router.put("/{bot_id}", response_model=BotInfo)
async def update_bot(
    request: Request,
    bot_id: str,
    data: BotUpdateRequest,
) -> Dict[str, Any]:
    """Update bot."""
    _get_current_user(request)
    bot = BOTS_DB.get(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail=f"Bot not found: {bot_id}")
    if data.bot_name:
        bot["bot_name"] = data.bot_name
    if data.config:
        bot["config"] = data.config
    if data.status:
        bot["status"] = data.status
    bot["updated_at"] = datetime.utcnow().isoformat() + "Z"
    return bot


@router.delete("/{bot_id}")
async def delete_bot(
    request: Request,
    bot_id: str,
) -> Dict[str, str]:
    """Delete bot."""
    _get_current_user(request)
    if bot_id not in BOTS_DB:
        raise HTTPException(status_code=404, detail=f"Bot not found: {bot_id}")
    del BOTS_DB[bot_id]
    return {"message": "Bot deleted successfully"}


@router.post("/connect")
async def connect_bot(
    request: Request,
    data: BotConnectRequest,
) -> Dict[str, str]:
    """Connect bot."""
    _get_current_user(request)
    bot = BOTS_DB.get(data.bot_id)
    if not bot:
        raise HTTPException(
            status_code=404,
            detail=f"Bot not found: {data.bot_id}",
        )
    bot["client_id"] = data.client_id
    bot["webhook_url"] = data.webhook_url
    bot["status"] = "connected"
    bot["connected_at"] = datetime.utcnow().isoformat() + "Z"
    bot["updated_at"] = datetime.utcnow().isoformat() + "Z"
    return {"message": "Bot connected successfully"}


@router.post("/{bot_id}/disconnect")
async def disconnect_bot(
    request: Request,
    bot_id: str,
) -> Dict[str, str]:
    """Disconnect bot."""
    _get_current_user(request)
    bot = BOTS_DB.get(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail=f"Bot not found: {bot_id}")
    bot["status"] = "disconnected"
    bot["updated_at"] = datetime.utcnow().isoformat() + "Z"
    return {"message": "Bot disconnected successfully"}


@router.get("/{bot_id}/status", response_model=BotStatusResponse)
async def get_bot_status(
    request: Request,
    bot_id: str,
) -> Dict[str, Any]:
    """Get bot status."""
    _get_current_user(request)
    bot = BOTS_DB.get(bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail=f"Bot not found: {bot_id}")
    return {
        "bot_id": bot_id,
        "status": bot.get("status"),
        "last_heartbeat": None,
        "message_count": 0,
        "error_count": 0,
    }
