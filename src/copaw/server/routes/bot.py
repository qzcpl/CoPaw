"""
Bot 管理 API
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime

from ..schemas.bot import (
    BotResponse,
    BotCreateRequest,
    BotUpdateRequest,
    BotConnectRequest,
    BotStatusResponse,
)
from ..core.exceptions import ApiError, ApiErrorCode
from ..dependencies import get_current_user

router = APIRouter()

# 模拟 Bot 数据库
BOTS_DB = {}


@router.get("", response_model=List[BotResponse])
async def list_bots(
    tenant_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    列出 Bot 列表
    
    Args:
        tenant_id: 租户 ID
        current_user: 当前用户
    
    Returns:
        Bot 列表
    """
    effective_tenant_id = tenant_id or current_user["tenant_id"]
    
    bots = [b for b in BOTS_DB.values() if b["tenant_id"] == effective_tenant_id]
    
    return bots


@router.get("/{bot_id}", response_model=BotResponse)
async def get_bot(
    bot_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    查询 Bot 详情
    
    Args:
        bot_id: Bot ID
        current_user: 当前用户
    
    Returns:
        Bot 详情
    """
    bot = BOTS_DB.get(bot_id)
    
    if not bot:
        raise ApiError(
            code=ApiErrorCode.BOT_NOT_FOUND,
            message=f"Bot not found: {bot_id}",
            status_code=404,
        )
    
    # 权限检查
    if bot["tenant_id"] != current_user["tenant_id"]:
        raise ApiError(
            code=ApiErrorCode.TENANT_ACCESS_DENIED,
            message="Access denied to this Bot",
            status_code=403,
        )
    
    return bot


@router.post("", response_model=BotResponse)
async def create_bot(
    request: BotCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    创建 Bot
    
    Args:
        request: 创建请求
        current_user: 当前用户
    
    Returns:
        创建的 Bot
    """
    # 权限检查
    if current_user["role"] not in ["tenant_admin", "system_admin"]:
        raise ApiError(
            code=ApiErrorCode.PERMISSION_DENIED,
            message="Only tenant admin can create Bot",
            status_code=403,
        )
    
    bot_id = f"bot_{request.bot_name}_{int(datetime.utcnow().timestamp())}"
    
    bot = {
        "bot_id": bot_id,
        "bot_name": request.bot_name,
        "tenant_id": request.tenant_id,
        "platform": request.platform,
        "status": "disconnected",
        "webhook_url": None,
        "client_id": None,
        "connected_at": None,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "config": request.config,
    }
    
    BOTS_DB[bot_id] = bot
    
    return bot


@router.put("/{bot_id}", response_model=BotResponse)
async def update_bot(
    bot_id: str,
    request: BotUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    更新 Bot
    
    Args:
        bot_id: Bot ID
        request: 更新请求
        current_user: 当前用户
    
    Returns:
        更新后的 Bot
    """
    bot = BOTS_DB.get(bot_id)
    
    if not bot:
        raise ApiError(
            code=ApiErrorCode.BOT_NOT_FOUND,
            message=f"Bot not found: {bot_id}",
            status_code=404,
        )
    
    # 权限检查
    if bot["tenant_id"] != current_user["tenant_id"]:
        raise ApiError(
            code=ApiErrorCode.TENANT_ACCESS_DENIED,
            message="Access denied to this Bot",
            status_code=403,
        )
    
    # 更新字段
    if request.bot_name:
        bot["bot_name"] = request.bot_name
    if request.config:
        bot["config"] = request.config
    bot["updated_at"] = datetime.utcnow().isoformat() + "Z"
    
    return bot


@router.delete("/{bot_id}")
async def delete_bot(
    bot_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    删除 Bot
    
    Args:
        bot_id: Bot ID
        current_user: 当前用户
    """
    bot = BOTS_DB.get(bot_id)
    
    if not bot:
        raise ApiError(
            code=ApiErrorCode.BOT_NOT_FOUND,
            message=f"Bot not found: {bot_id}",
            status_code=404,
        )
    
    # 权限检查
    if current_user["role"] not in ["tenant_admin", "system_admin"]:
        raise ApiError(
            code=ApiErrorCode.PERMISSION_DENIED,
            message="Only tenant admin can delete Bot",
            status_code=403,
        )
    
    if bot["tenant_id"] != current_user["tenant_id"]:
        raise ApiError(
            code=ApiErrorCode.TENANT_ACCESS_DENIED,
            message="Access denied to this Bot",
            status_code=403,
        )
    
    del BOTS_DB[bot_id]
    
    return {"message": "Bot deleted successfully"}


@router.post("/{bot_id}/connect")
async def connect_bot(
    bot_id: str,
    request: BotConnectRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    连接 Bot
    
    Args:
        bot_id: Bot ID
        request: 连接请求
        current_user: 当前用户
    """
    bot = BOTS_DB.get(bot_id)
    
    if not bot:
        raise ApiError(
            code=ApiErrorCode.BOT_NOT_FOUND,
            message=f"Bot not found: {bot_id}",
            status_code=404,
        )
    
    # 更新连接信息
    bot["client_id"] = request.client_id
    bot["webhook_url"] = request.webhook_url
    bot["status"] = "connected"
    bot["connected_at"] = datetime.utcnow().isoformat() + "Z"
    bot["updated_at"] = datetime.utcnow().isoformat() + "Z"
    
    return {"message": "Bot connected successfully"}


@router.get("/{bot_id}/status", response_model=BotStatusResponse)
async def get_bot_status(
    bot_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    查询 Bot 状态
    
    Args:
        bot_id: Bot ID
        current_user: 当前用户
    
    Returns:
        Bot 状态
    """
    bot = BOTS_DB.get(bot_id)
    
    if not bot:
        raise ApiError(
            code=ApiErrorCode.BOT_NOT_FOUND,
            message=f"Bot not found: {bot_id}",
            status_code=404,
        )
    
    return BotStatusResponse(
        bot_id=bot_id,
        status=bot["status"],
        last_heartbeat=datetime.fromisoformat(bot["connected_at"]) if bot["connected_at"] else None,
        message_count=0,
        error_count=0,
    )
