"""
聊天 API
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime

from ..schemas.chat import (
    BusMessageV3,
    SendMessageRequest,
    SendMessageResponse,
    SessionContextV2,
    SessionResponse,
    SessionListResponse,
)
from ..core.exceptions import ApiError, ApiErrorCode
from ..dependencies import get_current_user

router = APIRouter()

# 模拟会话数据库
SESSIONS_DB = {}
MESSAGES_DB = []


@router.post("/send", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    发送消息
    
    Args:
        request: 发送请求
        current_user: 当前用户
    
    Returns:
        发送响应
    """
    message_id = f"msg_{int(datetime.utcnow().timestamp())}_{len(MESSAGES_DB)}"
    
    # 创建消息
    message = {
        "message_id": message_id,
        "call_id": request.call_id,
        "content": request.content,
        "content_type": request.content_type,
        "metadata": request.metadata or {},
        "sender_id": current_user["user_id"],
        "tenant_id": current_user["tenant_id"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": "sent",
    }
    
    MESSAGES_DB.append(message)
    
    return SendMessageResponse(
        message_id=message_id,
        call_id=request.call_id,
        status="sent",
        timestamp=datetime.fromisoformat(message["timestamp"]),
    )


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    call_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    """
    列出会话
    
    Args:
        call_id: callId
        status: 会话状态
        page: 页码
        page_size: 每页数量
        current_user: 当前用户
    
    Returns:
        会话列表
    """
    sessions = list(SESSIONS_DB.values())
    
    # 过滤
    if call_id:
        sessions = [s for s in sessions if s["call_id"] == call_id]
    if status:
        sessions = [s for s in sessions if s["status"] == status]
    
    # 分页
    total = len(sessions)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = sessions[start:end]
    
    return SessionListResponse(
        sessions=paginated,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    查询会话详情
    
    Args:
        session_id: 会话 ID
        current_user: 当前用户
    
    Returns:
        会话详情
    """
    session = SESSIONS_DB.get(session_id)
    
    if not session:
        raise ApiError(
            code=ApiErrorCode.NOT_FOUND,
            message=f"Session not found: {session_id}",
            status_code=404,
        )
    
    return session


@router.get("/sessions/{session_id}/context")
async def get_session_context(
    session_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    查询会话上下文
    
    Args:
        session_id: 会话 ID
        current_user: 当前用户
    
    Returns:
        会话上下文
    """
    session = SESSIONS_DB.get(session_id)
    
    if not session:
        raise ApiError(
            code=ApiErrorCode.NOT_FOUND,
            message=f"Session not found: {session_id}",
            status_code=404,
        )
    
    # 返回上下文
    return session.get("context", {})


@router.post("/sessions/{session_id}/close")
async def close_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    关闭会话
    
    Args:
        session_id: 会话 ID
        current_user: 当前用户
    """
    session = SESSIONS_DB.get(session_id)
    
    if not session:
        raise ApiError(
            code=ApiErrorCode.NOT_FOUND,
            message=f"Session not found: {session_id}",
            status_code=404,
        )
    
    session["status"] = "closed"
    session["closed_at"] = datetime.utcnow().isoformat() + "Z"
    
    return {"message": "Session closed successfully"}


@router.get("/messages", response_model=List[BusMessageV3])
async def list_messages(
    session_id: str = Query(...),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    """
    列出消息
    
    Args:
        session_id: 会话 ID
        limit: 返回数量
        current_user: 当前用户
    
    Returns:
        消息列表
    """
    # 过滤消息
    messages = [m for m in MESSAGES_DB if m.get("session_id") == session_id]
    
    # 按时间倒序，限制数量
    messages = sorted(messages, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    # 转换为 BusMessageV3 格式
    result = []
    for msg in messages:
        result.append(BusMessageV3(
            message_id=msg["message_id"],
            channel_id=msg.get("channel_id", "unknown"),
            channel_type=msg.get("channel_type", "unknown"),
            caller_logical_id=msg.get("caller_logical_id", "unknown"),
            caller_physical_id=msg.get("caller_physical_id", msg["sender_id"]),
            called_id=msg.get("called_id", "unknown"),
            session_id=session_id,
            content_type=msg["content_type"],
            content=msg["content"],
            timestamp=datetime.fromisoformat(msg["timestamp"]),
            direction="outbound",
            metadata=msg.get("metadata", {}),
        ))
    
    return result
