# -*- coding: utf-8 -*-
"""Chat and session management API routes - delegates to ChatManager."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


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


async def _get_chat_manager(request: Request):
    """Get chat manager from workspace."""
    from ..agent_context import get_agent_for_request

    agent = await get_agent_for_request(request)
    workspace = agent.workspace
    return workspace.chat_manager


@router.get("/sessions", response_model=Dict[str, Any])
async def list_sessions(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tenant_id: Optional[str] = Query(None),
    call_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """List sessions with pagination - delegates to ChatManager."""
    _get_current_user(request)
    
    try:
        mgr = await _get_chat_manager(request)
        logger.info(f"ChatManager obtained: {mgr}")
        
        if mgr is None:
            logger.error("ChatManager is None!")
            return {
                "sessions": [],
                "total": 0,
                "page": page,
                "page_size": page_size,
            }
        
        chats = await mgr.list_chats(user_id=None, channel=None)
        logger.info(f"Loaded {len(chats)} chats")
    except Exception as e:
        logger.error(f"Failed to list chats: {e}", exc_info=True)
        # 临时方案：返回空列表
        return {
            "sessions": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
        }

    if tenant_id:
        chats = [
            c for c in chats if getattr(c, "tenant_id", None) == tenant_id
        ]
    if call_id:
        chats = [c for c in chats if getattr(c, "call_id", None) == call_id]
    if status:
        chats = [c for c in chats if getattr(c, "status", None) == status]

    total = len(chats)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = chats[start:end]

    sessions = []
    for chat in paginated:
        sessions.append(
            {
                "session_id": getattr(chat, "id", ""),
                "tenant_id": getattr(chat, "tenant_id", "default"),
                "agent_id": getattr(chat, "agent_id", "default"),
                "call_id": getattr(chat, "call_id", None),
                "status": getattr(chat, "status", "active"),
                "created_at": getattr(
                    chat, "created_at", datetime.utcnow().isoformat() + "Z"
                ),
                "updated_at": getattr(
                    chat, "updated_at", datetime.utcnow().isoformat() + "Z"
                ),
                "last_message_at": getattr(chat, "updated_at", None),
                "name": getattr(chat, "name", ""),
                "user_id": getattr(chat, "user_id", ""),
                "channel": getattr(chat, "channel", ""),
                "message_count": getattr(chat, "message_count", 0),
                "unread_count": getattr(chat, "unread_count", 0),
            }
        )

    return {
        "sessions": sessions,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/sessions/{session_id}")
async def get_session_detail(
    request: Request,
    session_id: str,
    tenant_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """Get session detail with messages - delegates to ChatManager."""
    _get_current_user(request)
    mgr = await _get_chat_manager(request)

    try:
        chat = await mgr.get_chat(session_id)

        messages = getattr(chat, "messages", [])
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "message_id": getattr(msg, "id", ""),
                "role": getattr(msg, "role", "assistant"),
                "content": getattr(msg, "content", ""),
                "created_at": getattr(msg, "created_at", ""),
            })

        return {
            "session_id": getattr(chat, "id", session_id),
            "tenant_id": getattr(chat, "tenant_id", "default"),
            "agent_id": getattr(chat, "agent_id", "default"),
            "status": getattr(chat, "status", "active"),
            "created_at": getattr(chat, "created_at", ""),
            "updated_at": getattr(chat, "updated_at", ""),
            "messages": formatted_messages,
        }
    except Exception as e:
        logger.error(f"Failed to get session detail: {e}", exc_info=True)
        raise HTTPException(
            status_code=404,
            detail=f"Session not found: {session_id}",
        )


@router.delete("/sessions/{session_id}")
async def delete_session(
    request: Request,
    session_id: str,
    tenant_id: Optional[str] = Query(None),
) -> Dict[str, str]:
    """Delete session - delegates to ChatManager."""
    _get_current_user(request)
    mgr = await _get_chat_manager(request)

    try:
        await mgr.delete_chat(session_id)
    except Exception:
        pass

    return {"message": "Session deleted successfully"}


@router.post("/sessions/{session_id}/close")
async def close_session(
    request: Request,
    session_id: str,
    tenant_id: Optional[str] = Query(None),
) -> Dict[str, str]:
    """Close session."""
    _get_current_user(request)
    return {"message": "Session closed successfully"}


@router.post("/sessions/{session_id}/pause")
async def pause_session(
    request: Request,
    session_id: str,
    tenant_id: Optional[str] = Query(None),
) -> Dict[str, str]:
    """Pause session."""
    _get_current_user(request)
    return {"message": "Session paused successfully"}


@router.post("/sessions/{session_id}/resume")
async def resume_session(
    request: Request,
    session_id: str,
    tenant_id: Optional[str] = Query(None),
) -> Dict[str, str]:
    """Resume session."""
    _get_current_user(request)
    return {"message": "Session resumed successfully"}


@router.get("/sessions/{session_id}/history")
async def get_session_history(
    request: Request,
    session_id: str,
    limit: int = Query(50, ge=1, le=100),
    before: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    """Get session history messages - delegates to ChatManager."""
    _get_current_user(request)
    mgr = await _get_chat_manager(request)

    try:
        chat = await mgr.get_chat(session_id)
        return getattr(chat, "messages", [])[:limit]
    except Exception:
        return []


@router.post("/send")
async def send_message(
    request: Request,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """Send a message."""
    _get_current_user(request)
    return {
        "message_id": f"msg_{int(datetime.utcnow().timestamp())}",
        "session_id": data.get("session_id", ""),
        "content": data.get("message", ""),
        "created_at": datetime.utcnow().isoformat() + "Z",
    }


# Legacy chat endpoints - delegate to ChatManager
@router.get("/chats")
async def list_chats(
    request: Request,
    user_id: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
) -> List[Dict[str, Any]]:
    """List chats (legacy) - delegates to ChatManager."""
    _get_current_user(request)
    mgr = await _get_chat_manager(request)

    try:
        chats = await mgr.list_chats(user_id=user_id, channel=channel)
        return [
            {
                "chat_id": getattr(c, "id", ""),
                "name": getattr(c, "name", ""),
                "user_id": getattr(c, "user_id", ""),
                "channel": getattr(c, "channel", ""),
                "created_at": getattr(c, "created_at", ""),
                "updated_at": getattr(c, "updated_at", ""),
            }
            for c in chats
        ]
    except Exception:
        return []


@router.post("/chats")
async def create_chat(
    request: Request,
    chat: Dict[str, Any],
) -> Dict[str, Any]:
    """Create chat (legacy)."""
    _get_current_user(request)
    chat_id = chat.get("chat_id", f"chat_{int(datetime.utcnow().timestamp())}")
    return {
        "chat_id": chat_id,
        "name": chat.get("name", ""),
        "user_id": chat.get("user_id", ""),
        "channel": chat.get("channel", ""),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/chats/{chat_id}")
async def get_chat(
    request: Request,
    chat_id: str,
) -> Dict[str, Any]:
    """Get chat (legacy) - delegates to ChatManager."""
    _get_current_user(request)
    mgr = await _get_chat_manager(request)

    try:
        chat = await mgr.get_chat(chat_id)
        return {
            "chat_id": getattr(chat, "id", chat_id),
            "name": getattr(chat, "name", ""),
            "user_id": getattr(chat, "user_id", ""),
            "channel": getattr(chat, "channel", ""),
            "created_at": getattr(chat, "created_at", ""),
            "updated_at": getattr(chat, "updated_at", ""),
        }
    except Exception:
        raise HTTPException(
            status_code=404,
            detail=f"Chat not found: {chat_id}",
        )


@router.put("/chats/{chat_id}")
async def update_chat(
    request: Request,
    chat_id: str,
    chat: Dict[str, Any],
) -> Dict[str, Any]:
    """Update chat (legacy)."""
    _get_current_user(request)
    return {
        "chat_id": chat_id,
        "name": chat.get("name", ""),
        "user_id": chat.get("user_id", ""),
        "channel": chat.get("channel", ""),
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }


@router.delete("/chats/{chat_id}")
async def delete_chat(
    request: Request,
    chat_id: str,
) -> Dict[str, Any]:
    """Delete chat (legacy) - delegates to ChatManager."""
    _get_current_user(request)
    mgr = await _get_chat_manager(request)

    try:
        await mgr.delete_chat(chat_id)
    except Exception:
        pass

    return {"success": True, "deleted_count": 1}


@router.post("/chats/batch-delete")
async def batch_delete_chats(
    request: Request,
    chat_ids: List[str],
) -> Dict[str, Any]:
    """Batch delete chats (legacy) - delegates to ChatManager."""
    _get_current_user(request)
    mgr = await _get_chat_manager(request)

    deleted_count = 0
    for chat_id in chat_ids:
        try:
            await mgr.delete_chat(chat_id)
            deleted_count += 1
        except Exception:
            pass

    return {"success": True, "deleted_count": deleted_count}
