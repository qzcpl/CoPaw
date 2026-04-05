# -*- coding: utf-8 -*-
"""
Channel schema: channel type identifiers, routing (ChannelAddress),
and conversion protocol.

v2.0: 添加 BusMessage v3 和 SessionContext v2，支持六层标识体系和会话穿透
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable, Literal
from datetime import datetime


@dataclass
class ChannelAddress:
    """
    Unified routing for send: kind + id + extra.
    Replaces ad-hoc meta keys (channel_id, user_id, session_webhook, etc.).
    """

    kind: str  # "dm" | "channel" | "webhook" | "console" | ...
    id: str
    extra: Optional[Dict[str, Any]] = None

    def to_handle(self) -> str:
        """String handle for to_handle (e.g. discord:ch:123)."""
        if self.extra and "to_handle" in self.extra:
            return str(self.extra["to_handle"])
        return f"{self.kind}:{self.id}"


# Built-in channel type identifiers. Plugin channels use arbitrary str keys.
BUILTIN_CHANNEL_TYPES = (
    "imessage",
    "discord",
    "dingtalk",
    "feishu",
    "qq",
    "telegram",
    "mqtt",
    "console",
    "voice",
    "xiaoyi",
)

# ChannelType is str to allow plugin channels; built-in set above.
ChannelType = str

# Default channel when none is specified (runner / config).
DEFAULT_CHANNEL: ChannelType = "console"


@runtime_checkable
class ChannelMessageConverter(Protocol):
    """
    Protocol for channel message conversion.
    Channels convert native payloads to AgentRequest and send responses.
    """

    def build_agent_request_from_native(self, native_payload: Any) -> Any:
        """
        Convert this channel's native message payload to AgentRequest.
        Use runtime Message and Content types; no intermediate envelope.
        """

    async def send_response(
        self,
        to_handle: str,
        response: Any,
        meta: Optional[dict] = None,
    ) -> None:
        """Convert AgentResponse to channel reply and send."""


# ============================================================
# BusMessage v3 - 支持六层标识体系
# ============================================================

@dataclass
class BusMessage:
    """
    BusMessage v3 - 总线消息
    
    支持六层标识体系和会话穿透，用于频道与 Agent 之间的消息传递
    
    Attributes:
        message_id: L6 消息层标识符
        channel_id: L1 传输层标识符
        caller_logical_id: L2 逻辑主叫层标识符
        caller_physical_id: L3 物理主叫层标识符
        called_id: L4 被叫层标识符
        session_id: L5 会话层标识符
        channel_type: 会话类型（private/group）
        content: 消息内容
        content_type: 内容类型（text/image/file 等）
        timestamp: 消息时间戳
        meta: 元数据（扩展字段）
    """
    
    # 六层标识符
    message_id: str
    channel_id: str
    caller_logical_id: str
    caller_physical_id: str
    called_id: str
    session_id: str
    
    # 会话类型
    channel_type: Literal["private", "group"] = "private"
    
    # 消息内容
    content: Any = None
    content_type: str = "text"  # text, image, file, voice, video
    
    # 元数据
    timestamp: datetime = field(default_factory=datetime.now)
    meta: Optional[Dict[str, Any]] = None
    
    # 群聊相关字段（仅群聊场景）
    group_id: Optional[str] = None  # 群 ID（冗余，等于 caller_logical_id 去掉前缀）
    group_name: Optional[str] = None  # 群名称
    sender_name: Optional[str] = None  # 发送者名称
    mention_info: Optional[Dict[str, Any]] = None  # 提及信息
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "message_id": self.message_id,
            "channel_id": self.channel_id,
            "caller_logical_id": self.caller_logical_id,
            "caller_physical_id": self.caller_physical_id,
            "called_id": self.called_id,
            "session_id": self.session_id,
            "channel_type": self.channel_type,
            "content": self.content,
            "content_type": self.content_type,
            "timestamp": self.timestamp.isoformat(),
            "meta": self.meta,
            "group_id": self.group_id,
            "group_name": self.group_name,
            "sender_name": self.sender_name,
            "mention_info": self.mention_info,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BusMessage:
        """从字典创建"""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.now()
        
        return cls(
            message_id=data["message_id"],
            channel_id=data["channel_id"],
            caller_logical_id=data["caller_logical_id"],
            caller_physical_id=data["caller_physical_id"],
            called_id=data["called_id"],
            session_id=data["session_id"],
            channel_type=data.get("channel_type", "private"),
            content=data.get("content"),
            content_type=data.get("content_type", "text"),
            timestamp=timestamp,
            meta=data.get("meta"),
            group_id=data.get("group_id"),
            group_name=data.get("group_name"),
            sender_name=data.get("sender_name"),
            mention_info=data.get("mention_info"),
        )
    
    def is_group_message(self) -> bool:
        """是否为群聊消息"""
        return self.channel_type == "group"
    
    def is_private_message(self) -> bool:
        """是否为私聊消息"""
        return self.channel_type == "private"
    
    def get_identifiers(self) -> Dict[str, str]:
        """获取六层标识符"""
        return {
            "channel_id": self.channel_id,
            "caller_logical_id": self.caller_logical_id,
            "caller_physical_id": self.caller_physical_id,
            "called_id": self.called_id,
            "session_id": self.session_id,
            "message_id": self.message_id,
        }
    
    def __str__(self) -> str:
        return (
            f"BusMessage(id={self.message_id}, "
            f"channel={self.channel_id}, "
            f"from={self.caller_logical_id}, "
            f"to={self.called_id}, "
            f"session={self.session_id})"
        )


# ============================================================
# SessionContext v2 - 会话上下文（会话穿透）
# ============================================================

@dataclass
class UserProfile:
    """
    用户画像
    
    Attributes:
        user_id: 用户 ID
        name: 用户名称
        avatar: 头像 URL
        tags: 用户标签
        preferences: 用户偏好
        metadata: 扩展元数据
    """
    user_id: str
    name: Optional[str] = None
    avatar: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GroupContext:
    """
    群聊上下文
    
    Attributes:
        group_id: 群 ID
        group_name: 群名称
        member_count: 成员数
        members: 成员列表
        group_type: 群类型
        metadata: 扩展元数据
    """
    group_id: str
    group_name: Optional[str] = None
    member_count: int = 0
    members: List[Dict[str, Any]] = field(default_factory=list)
    group_type: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionContext:
    """
    SessionContext v2 - 会话上下文（会话穿透）
    
    让 Agent 知道完整的对话上下文：谁发的、发给谁、什么渠道、聊到哪
    
    Attributes:
        channel: 频道信息
        caller_logical_id: 逻辑主叫 ID（会话主体）
        caller_physical_id: 物理主叫 ID（实际发送者）
        called_id: 被叫 ID
        session_id: 会话 ID
        user_profile: 用户画像
        group_context: 群聊上下文（仅群聊场景）
        conversation_history: 对话历史摘要
        metadata: 扩展元数据
    """
    
    # 六层标识符（核心）
    channel: str  # channel_id
    caller_logical_id: str
    caller_physical_id: str
    called_id: str
    session_id: str
    
    # 用户画像（可选，缓存或数据库加载）
    user_profile: Optional[UserProfile] = None
    
    # 群聊上下文（仅群聊场景）
    group_context: Optional[GroupContext] = None
    
    # 对话历史摘要（可选，用于上下文理解）
    conversation_history: Optional[str] = None
    
    # 扩展元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "channel": self.channel,
            "caller_logical_id": self.caller_logical_id,
            "caller_physical_id": self.caller_physical_id,
            "called_id": self.called_id,
            "session_id": self.session_id,
            "user_profile": self.user_profile.__dict__ if self.user_profile else None,
            "group_context": self.group_context.__dict__ if self.group_context else None,
            "conversation_history": self.conversation_history,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SessionContext:
        """从字典创建"""
        user_profile = None
        if data.get("user_profile"):
            user_profile = UserProfile(**data["user_profile"])
        
        group_context = None
        if data.get("group_context"):
            group_context = GroupContext(**data["group_context"])
        
        return cls(
            channel=data["channel"],
            caller_logical_id=data["caller_logical_id"],
            caller_physical_id=data["caller_physical_id"],
            called_id=data["called_id"],
            session_id=data["session_id"],
            user_profile=user_profile,
            group_context=group_context,
            conversation_history=data.get("conversation_history"),
            metadata=data.get("metadata", {}),
        )
    
    def is_group_session(self) -> bool:
        """是否为群聊会话"""
        return self.group_context is not None
    
    def get_display_name(self) -> str:
        """获取显示名称"""
        if self.group_context:
            return self.group_context.group_name or self.group_context.group_id
        elif self.user_profile:
            return self.user_profile.name or self.user_profile.user_id
        else:
            return self.caller_physical_id
    
    def __str__(self) -> str:
        context_type = "group" if self.is_group_session() else "private"
        return (
            f"SessionContext(type={context_type}, "
            f"channel={self.channel}, "
            f"from={self.caller_logical_id}, "
            f"to={self.called_id}, "
            f"session={self.session_id})"
        )


# ============================================================
# 辅助函数
# ============================================================

def create_bus_message_from_identifiers(
    identifiers: Dict[str, str],
    content: Any,
    content_type: str = "text",
    **kwargs,
) -> BusMessage:
    """
    从标识符创建 BusMessage
    
    Args:
        identifiers: 六层标识符字典
        content: 消息内容
        content_type: 内容类型
        **kwargs: 其他参数（meta, group_id 等）
    
    Returns:
        BusMessage 对象
    """
    return BusMessage(
        message_id=identifiers["message_id"],
        channel_id=identifiers["channel_id"],
        caller_logical_id=identifiers["caller_logical_id"],
        caller_physical_id=identifiers["caller_physical_id"],
        called_id=identifiers["called_id"],
        session_id=identifiers["session_id"],
        channel_type=identifiers.get("channel_type", "private"),
        content=content,
        content_type=content_type,
        **kwargs,
    )


def create_session_context_from_bus_message(
    message: BusMessage,
    user_profile: Optional[UserProfile] = None,
    group_context: Optional[GroupContext] = None,
) -> SessionContext:
    """
    从 BusMessage 创建 SessionContext
    
    Args:
        message: BusMessage 对象
        user_profile: 用户画像（可选）
        group_context: 群聊上下文（可选）
    
    Returns:
        SessionContext 对象
    """
    return SessionContext(
        channel=message.channel_id,
        caller_logical_id=message.caller_logical_id,
        caller_physical_id=message.caller_physical_id,
        called_id=message.called_id,
        session_id=message.session_id,
        user_profile=user_profile,
        group_context=group_context,
    )
