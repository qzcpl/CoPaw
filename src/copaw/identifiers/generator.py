"""
标识符生成器

生成符合规范的六层标识符
"""

import uuid
import time
from typing import Optional
from .schemas import (
    ChannelId,
    CallerLogicalId,
    CallerPhysicalId,
    CalledId,
    SessionId,
    MessageId,
    Identifiers,
    CallerType,
)


class IdentifierGenerator:
    """
    标识符生成器
    
    生成符合规范的六层标识符，支持私聊和群聊场景
    """
    
    def __init__(self, prefix: str = "copaw"):
        """
        Args:
            prefix: 标识符前缀，用于区分不同系统
        """
        self.prefix = prefix
    
    def generate_channel_id(self, channel_type: str) -> ChannelId:
        """
        生成频道 ID
        
        Args:
            channel_type: 频道类型（dingtalk/feishu/wecom 等）
        
        Returns:
            ChannelId 对象
        """
        return ChannelId(channel_type.lower())
    
    def generate_caller_logical_id(
        self,
        caller_type: CallerType,
        unique_id: Optional[str] = None,
    ) -> CallerLogicalId:
        """
        生成逻辑主叫 ID
        
        Args:
            caller_type: 主叫类型（user/group/system/bot）
            unique_id: 唯一 ID（可选，默认生成 UUID）
        
        Returns:
            CallerLogicalId 对象
        """
        if unique_id is None:
            unique_id = uuid.uuid4().hex[:12]
        
        value = f"{caller_type.value}_{unique_id}"
        return CallerLogicalId(value, caller_type)
    
    def generate_caller_physical_id(
        self,
        user_id: Optional[str] = None,
    ) -> CallerPhysicalId:
        """
        生成物理主叫 ID
        
        Args:
            user_id: 用户 ID（可选，默认生成 UUID）
        
        Returns:
            CallerPhysicalId 对象
        """
        if user_id is None:
            user_id = uuid.uuid4().hex[:12]
        
        value = f"user_{user_id}"
        return CallerPhysicalId(value)
    
    def generate_called_id(
        self,
        prefix: str = "400",
        number: Optional[str] = None,
    ) -> CalledId:
        """
        生成被叫 ID
        
        Args:
            prefix: 前缀（如 400/800）
            number: 号码（可选，默认生成随机数）
        
        Returns:
            CalledId 对象
        """
        if number is None:
            number = f"{uuid.uuid4().int % 10000:04d}"
        
        value = f"{prefix}-{number}"
        return CalledId(value)
    
    def generate_session_id(
        self,
        caller_id: Optional[str] = None,
        timestamp: Optional[float] = None,
    ) -> SessionId:
        """
        生成会话 ID
        
        Args:
            caller_id: 主叫 ID（可选，用于生成有意义的 session_id）
            timestamp: 时间戳（可选，默认当前时间）
        
        Returns:
            SessionId 对象
        """
        if caller_id:
            # 使用 caller_id + 时间戳生成
            ts = int(timestamp or time.time())
            value = f"{caller_id}_{ts}"
        else:
            # 使用 UUID 生成
            value = f"session_{uuid.uuid4().hex}"
        
        return SessionId(value)
    
    def generate_message_id(
        self,
        channel_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        seq: int = 0,
    ) -> MessageId:
        """
        生成消息 ID
        
        Args:
            channel_id: 频道 ID（可选，用于生成有意义的 message_id）
            timestamp: 时间戳（可选，默认当前时间）
            seq: 序列号（用于区分同一时刻的多条消息）
        
        Returns:
            MessageId 对象
        """
        if channel_id and timestamp:
            # 使用 channel_id + 时间戳 + 序列号生成
            ts = int(timestamp)
            value = f"{channel_id}_{ts}_{seq:06d}"
        else:
            # 使用 UUID 生成
            value = f"msg_{uuid.uuid4().hex}"
        
        return MessageId(value)
    
    def generate_private_identifiers(
        self,
        channel_type: str,
        user_id: str,
        called_id: str,
    ) -> Identifiers:
        """
        生成私聊场景的六层标识符
        
        Args:
            channel_type: 频道类型（dingtalk/feishu 等）
            user_id: 用户 ID（不含前缀）
            called_id: 被叫 ID
        
        Returns:
            Identifiers 对象
        """
        channel_id = self.generate_channel_id(channel_type)
        # user_id 可能已包含前缀，需要处理
        clean_user_id = user_id.replace("user_", "", 1) if user_id.startswith("user_") else user_id
        caller_logical = self.generate_caller_logical_id(
            CallerType.USER, clean_user_id
        )
        caller_physical = self.generate_caller_physical_id(clean_user_id)
        called = CalledId(called_id)
        session = self.generate_session_id(clean_user_id)
        message = self.generate_message_id(channel_type)
        
        return Identifiers(
            channel_id=channel_id,
            caller_logical_id=caller_logical,
            caller_physical_id=caller_physical,
            called_id=called,
            session_id=session,
            message_id=message,
            channel_type="private",
        )
    
    def generate_group_identifiers(
        self,
        channel_type: str,
        group_id: str,
        user_id: str,
        called_id: str,
    ) -> Identifiers:
        """
        生成群聊场景的六层标识符
        
        Args:
            channel_type: 频道类型（dingtalk/feishu 等）
            group_id: 群 ID（不含前缀）
            user_id: 用户 ID（不含前缀）
            called_id: 被叫 ID
        
        Returns:
            Identifiers 对象
        """
        channel_id = self.generate_channel_id(channel_type)
        # 清理前缀
        clean_group_id = group_id.replace("group_", "", 1) if group_id.startswith("group_") else group_id
        clean_user_id = user_id.replace("user_", "", 1) if user_id.startswith("user_") else user_id
        caller_logical = self.generate_caller_logical_id(
            CallerType.GROUP, clean_group_id
        )
        caller_physical = self.generate_caller_physical_id(clean_user_id)
        called = CalledId(called_id)
        session = self.generate_session_id(f"{clean_group_id}_{clean_user_id}")
        message = self.generate_message_id(channel_type)
        
        return Identifiers(
            channel_id=channel_id,
            caller_logical_id=caller_logical,
            caller_physical_id=caller_physical,
            called_id=called,
            session_id=session,
            message_id=message,
            channel_type="group",
        )
    
    def regenerate_message_id(
        self,
        identifiers: Identifiers,
    ) -> Identifiers:
        """
        重新生成消息 ID（用于重试场景）
        
        Args:
            identifiers: 原标识符集合
        
        Returns:
            新的标识符集合（仅 message_id 不同）
        """
        new_message_id = self.generate_message_id(
            str(identifiers.channel_id)
        )
        
        return Identifiers(
            channel_id=identifiers.channel_id,
            caller_logical_id=identifiers.caller_logical_id,
            caller_physical_id=identifiers.caller_physical_id,
            called_id=identifiers.called_id,
            session_id=identifiers.session_id,
            message_id=new_message_id,
            channel_type=identifiers.channel_type,
        )
