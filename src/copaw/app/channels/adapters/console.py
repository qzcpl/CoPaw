# -*- coding: utf-8 -*-
"""
Console 适配器

实现 Console 频道消息与 BusMessage v3 之间的转换

【TODO】阶段二完成后扩展更多功能
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

patch_src = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(patch_src))

from copaw.identifiers.schemas import (
    Identifiers,
    ChannelId,
    CallerLogicalId,
    CallerPhysicalId,
    CalledId,
    SessionId,
    MessageId,
    CallerType,
)
from copaw.app.channels.schema import BusMessage, SessionContext

from .base import BaseAdapter


class ConsoleAdapter(BaseAdapter):
    """
    Console 适配器

    用于 Web Console 控制台的消息交互

    六层标识符映射：
    - channel_id: "console"
    - caller_logical_id: 从 session 获取（格式：user_{username}）
    - caller_physical_id: 同 caller_logical_id（私聊场景）
    - called_id: 从 session 获取（格式：agent_{agent_id}）
    - session_id: 从 session 获取
    - message_id: 自动生成
    """

    PLATFORM_ID = "console"
    SUPPORTS_MARKDOWN = True
    SUPPORTS_IMAGE = False
    SUPPORTS_FILE = False
    SUPPORTS_VOICE = False

    def _init_config(self):
        """初始化配置"""
        self.agent_id = self.config.get("agent_id", "default")
        self.default_user = self.config.get("default_user", "anonymous")

    async def convert_to_bus_message(
        self,
        raw_message: Dict[str, Any],
    ) -> BusMessage:
        """
        Console 消息 → BusMessage v3

        Args:
            raw_message: Console 原始消息，包含：
                - content: 消息内容
                - user_id: 用户 ID（可选）
                - session_id: 会话 ID（可选）
                - agent_id: Agent ID（可选）

        Returns:
            BusMessage v3
        """
        user_id = raw_message.get("user_id", self.default_user)
        session_id = (
            raw_message.get(
                "session_id",
                raw_message.get("session", {}).get("id")
                if isinstance(raw_message.get("session"), dict)
                else None,
            )
            or self._generate_session_id()
        )
        agent_id = raw_message.get("agent_id", self.agent_id)

        identifiers = Identifiers(
            channel_id=ChannelId(self.PLATFORM_ID),
            caller_logical_id=CallerLogicalId(
                f"user_{user_id}",
                caller_type=CallerType.USER,
            ),
            caller_physical_id=CallerPhysicalId(f"user_{user_id}"),
            called_id=CalledId(f"agent_{agent_id}"),
            session_id=SessionId(session_id),
            message_id=MessageId(self._generate_message_id()),
            channel_type="private",
        )

        content = raw_message.get("content", "")
        content_type = raw_message.get("content_type", "text")

        return BusMessage(
            message_id=str(identifiers.message_id),
            channel_id=str(identifiers.channel_id),
            caller_logical_id=str(identifiers.caller_logical_id),
            caller_physical_id=str(identifiers.caller_physical_id),
            called_id=str(identifiers.called_id),
            session_id=str(identifiers.session_id),
            channel_type="private",
            content=content,
            content_type=content_type,
            timestamp=datetime.now(),
            meta=raw_message.get("meta"),
        )

    async def convert_from_bus_message(
        self,
        message: BusMessage,
    ) -> Dict[str, Any]:
        """
        BusMessage v3 → Console 消息

        Args:
            message: BusMessage v3

        Returns:
            Console 格式消息
        """
        return {
            "content": message.content,
            "content_type": message.content_type,
            "user_id": message.caller_physical_id.replace("user_", "", 1),
            "session_id": message.session_id,
            "agent_id": message.called_id.replace("agent_", "", 1),
            "channel_id": message.channel_id,
            "message_id": message.message_id,
            "timestamp": message.timestamp.isoformat(),
            "channel_type": message.channel_type,
        }

    def validate_message(self, raw_message: Dict[str, Any]) -> bool:
        """
        验证 Console 消息有效性

        Args:
            raw_message: Console 原始消息

        Returns:
            是否有效
        """
        if not isinstance(raw_message, dict):
            return False
        if "content" not in raw_message and "content" not in str(raw_message):
            return False
        return True
