"""
六层标识体系数据结构

定义六层标识符的类型、格式和验证规则
"""

import re
import uuid
from dataclasses import dataclass, field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class ChannelType(str, Enum):
    """频道类型"""
    DINGTALK = "dingtalk"
    FEISHU = "feishu"
    WECOM = "wecom"
    PHONE = "phone"
    WEB = "web"
    EMAIL = "email"
    CONSOLE = "console"
    CUSTOM = "custom"


class CallerType(str, Enum):
    """主叫类型"""
    USER = "user"           # 用户
    GROUP = "group"         # 群组
    SYSTEM = "system"       # 系统
    BOT = "bot"            # 机器人


class ChannelType(str, Enum):
    """会话类型"""
    PRIVATE = "private"     # 私聊
    GROUP = "group"         # 群聊
    SYSTEM = "system"       # 系统消息


# ============================================================
# 六层标识符定义
# ============================================================

@dataclass(frozen=True)
class ChannelId:
    """
    L1: 传输层标识符 - 频道 ID
    
    标识消息传输通道，如 dingtalk/feishu/wecom 等
    
    格式：channel_id
    示例：dingtalk, feishu, wecom, phone, web, email, console
    """
    value: str
    
    def __post_init__(self):
        # 验证格式
        if not re.match(r'^[a-z][a-z0-9_]*$', self.value):
            raise ValueError(
                f"Invalid channel_id format: {self.value}. "
                "Must be lowercase letters, numbers, and underscores, starting with a letter."
            )
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CallerLogicalId:
    """
    L2: 逻辑主叫层标识符 - 逻辑主叫 ID
    
    会话发起方（会话主体）
    - 私聊场景：等于用户 ID
    - 群聊场景：等于群 ID
    
    格式：{type}_{uuid}
    示例：user_abc123, group_xyz789
    """
    value: str
    caller_type: CallerType = field(default=CallerType.USER)
    
    def __post_init__(self):
        # 验证格式（支持字母、数字、下划线、连字符）
        pattern = r'^(user|group|system|bot)_[a-zA-Z0-9_-]+$'
        if not re.match(pattern, self.value):
            raise ValueError(
                f"Invalid caller_logical_id format: {self.value}. "
                "Must be {type}_{id}, where type is user/group/system/bot."
            )
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def is_group(self) -> bool:
        """是否为群聊场景"""
        return self.caller_type == CallerType.GROUP
    
    @property
    def is_private(self) -> bool:
        """是否为私聊场景"""
        return self.caller_type == CallerType.USER


@dataclass(frozen=True)
class CallerPhysicalId:
    """
    L3: 物理主叫层标识符 - 物理主叫 ID
    
    实际发送消息的人
    - 私聊场景：等于 caller_logical_id
    - 群聊场景：等于实际发送者的用户 ID
    
    格式：user_{uuid}
    示例：user_abc123
    """
    value: str
    
    def __post_init__(self):
        # 验证格式（支持字母、数字、下划线、连字符）
        pattern = r'^user_[a-zA-Z0-9_-]+$'
        if not re.match(pattern, self.value):
            raise ValueError(
                f"Invalid caller_physical_id format: {self.value}. "
                "Must be user_{id}."
            )
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CalledId:
    """
    L4: 被叫层标识符 - 被叫 ID
    
    用户拨打的号码，绑定到具体 Agent
    支持"携号转网"（called_id 不变，背后 Agent 可切换）
    
    格式：{prefix}-{number} 或 {uuid}
    示例：400-001, 800-123, agent_abc123
    """
    value: str
    
    def __post_init__(self):
        # 验证格式（支持两种格式）
        pattern1 = r'^[0-9]{3,4}-[0-9]{3,4}$'  # 400-001
        pattern2 = r'^[a-z][a-z0-9_]*$'         # agent_abc123
        if not (re.match(pattern1, self.value) or re.match(pattern2, self.value)):
            raise ValueError(
                f"Invalid called_id format: {self.value}. "
                "Must be {prefix}-{number} (e.g., 400-001) or {uuid}."
            )
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SessionId:
    """
    L5: 会话层标识符 - 会话 ID
    
    一次完整对话的唯一标识
    
    格式：session_{uuid} 或 {caller_id}_{timestamp}
    示例：session_abc123xyz, user_001_1711900800
    """
    value: str
    
    def __post_init__(self):
        # 验证格式
        pattern = r'^[a-zA-Z0-9_-]+$'
        if not re.match(pattern, self.value):
            raise ValueError(
                f"Invalid session_id format: {self.value}. "
                "Must be alphanumeric with underscores and hyphens."
            )
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class MessageId:
    """
    L6: 消息层标识符 - 消息 ID
    
    单条消息的唯一标识
    
    格式：msg_{uuid} 或 {channel}_{timestamp}_{seq}
    示例：msg_abc123xyz, dingtalk_1711900800_001
    """
    value: str
    
    def __post_init__(self):
        # 验证格式
        pattern = r'^[a-zA-Z0-9_-]+$'
        if not re.match(pattern, self.value):
            raise ValueError(
                f"Invalid message_id format: {self.value}. "
                "Must be alphanumeric with underscores and hyphens."
            )
    
    def __str__(self) -> str:
        return self.value


# ============================================================
# 六层标识符集合
# ============================================================

@dataclass
class Identifiers:
    """
    六层标识符集合
    
    包含完整的六层标识体系，用于消息路由和会话追踪
    """
    channel_id: ChannelId
    caller_logical_id: CallerLogicalId
    caller_physical_id: CallerPhysicalId
    called_id: CalledId
    session_id: SessionId
    message_id: MessageId
    
    # 会话类型（私聊/群聊）
    channel_type: Literal["private", "group"] = field(default="private")
    
    def __post_init__(self):
        # 验证会话类型一致性
        if self.caller_logical_id.is_group:
            if self.channel_type != "group":
                raise ValueError(
                    "caller_logical_id is group but channel_type is not 'group'"
                )
            # 群聊场景：逻辑 caller 和物理 caller 应该不同
            if self.caller_logical_id.value == self.caller_physical_id.value:
                raise ValueError(
                    "In group chat, caller_logical_id should differ from caller_physical_id"
                )
        else:
            if self.channel_type != "private":
                raise ValueError(
                    "caller_logical_id is user but channel_type is not 'private'"
                )
            # 私聊场景：逻辑 caller 和物理 caller 应该相同
            if self.caller_logical_id.value != self.caller_physical_id.value:
                raise ValueError(
                    "In private chat, caller_logical_id should equal caller_physical_id"
                )
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "channel_id": str(self.channel_id),
            "caller_logical_id": str(self.caller_logical_id),
            "caller_physical_id": str(self.caller_physical_id),
            "called_id": str(self.called_id),
            "session_id": str(self.session_id),
            "message_id": str(self.message_id),
            "channel_type": self.channel_type,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Identifiers":
        """从字典创建"""
        return cls(
            channel_id=ChannelId(data["channel_id"]),
            caller_logical_id=CallerLogicalId(
                data["caller_logical_id"],
                caller_type=CallerType(data.get("caller_type", "user"))
            ),
            caller_physical_id=CallerPhysicalId(data["caller_physical_id"]),
            called_id=CalledId(data["called_id"]),
            session_id=SessionId(data["session_id"]),
            message_id=MessageId(data["message_id"]),
            channel_type=data.get("channel_type", "private"),
        )
    
    def __str__(self) -> str:
        return (
            f"Identifiers(channel={self.channel_id}, "
            f"logical={self.caller_logical_id}, "
            f"physical={self.caller_physical_id}, "
            f"called={self.called_id}, "
            f"session={self.session_id}, "
            f"message={self.message_id})"
        )


# ============================================================
# 辅助函数
# ============================================================

def create_private_identifiers(
    channel_id: str,
    user_id: str,
    called_id: str,
) -> Identifiers:
    """
    创建私聊场景的六层标识符
    
    Args:
        channel_id: 频道 ID
        user_id: 用户 ID（不含前缀）
        called_id: 被叫 ID
    
    Returns:
        Identifiers 对象
    """
    import uuid
    # 清理前缀
    clean_user_id = user_id.replace("user_", "", 1) if user_id.startswith("user_") else user_id
    
    return Identifiers(
        channel_id=ChannelId(channel_id),
        caller_logical_id=CallerLogicalId(f"user_{clean_user_id}", CallerType.USER),
        caller_physical_id=CallerPhysicalId(f"user_{clean_user_id}"),
        called_id=CalledId(called_id),
        session_id=SessionId(f"session_{uuid.uuid4().hex[:12]}"),
        message_id=MessageId(f"msg_{uuid.uuid4().hex[:12]}"),
        channel_type="private",
    )


def create_group_identifiers(
    channel_id: str,
    group_id: str,
    user_id: str,
    called_id: str,
) -> Identifiers:
    """
    创建群聊场景的六层标识符
    
    Args:
        channel_id: 频道 ID
        group_id: 群 ID（不含前缀）
        user_id: 用户 ID（不含前缀）
        called_id: 被叫 ID
    
    Returns:
        Identifiers 对象
    """
    import uuid
    # 清理前缀
    clean_group_id = group_id.replace("group_", "", 1) if group_id.startswith("group_") else group_id
    clean_user_id = user_id.replace("user_", "", 1) if user_id.startswith("user_") else user_id
    
    return Identifiers(
        channel_id=ChannelId(channel_id),
        caller_logical_id=CallerLogicalId(f"group_{clean_group_id}", CallerType.GROUP),
        caller_physical_id=CallerPhysicalId(f"user_{clean_user_id}"),
        called_id=CalledId(called_id),
        session_id=SessionId(f"session_{uuid.uuid4().hex[:12]}"),
        message_id=MessageId(f"msg_{uuid.uuid4().hex[:12]}"),
        channel_type="group",
    )
