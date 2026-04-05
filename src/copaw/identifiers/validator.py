"""
标识符验证器

验证六层标识符的格式和一致性
"""

import re
from typing import Tuple, Optional
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


class ValidationError(Exception):
    """验证异常"""
    pass


class IdentifierValidator:
    """
    标识符验证器
    
    验证六层标识符的格式和一致性
    """
    
    @staticmethod
    def validate_channel_id(value: str) -> Tuple[bool, Optional[str]]:
        """
        验证频道 ID
        
        Args:
            value: 频道 ID 字符串
        
        Returns:
            (是否有效，错误信息)
        """
        if not value:
            return False, "Channel ID cannot be empty"
        
        pattern = r'^[a-z][a-z0-9_]*$'
        if not re.match(pattern, value):
            return False, (
                f"Invalid channel_id format: {value}. "
                "Must be lowercase letters, numbers, and underscores, starting with a letter."
            )
        
        return True, None
    
    @staticmethod
    def validate_caller_logical_id(value: str) -> Tuple[bool, Optional[str]]:
        """
        验证逻辑主叫 ID
        
        Args:
            value: 逻辑主叫 ID 字符串
        
        Returns:
            (是否有效，错误信息)
        """
        if not value:
            return False, "Caller logical ID cannot be empty"
        
        pattern = r'^(user|group|system|bot)_[a-zA-Z0-9]+$'
        if not re.match(pattern, value):
            return False, (
                f"Invalid caller_logical_id format: {value}. "
                "Must be {type}_{id}, where type is user/group/system/bot."
            )
        
        return True, None
    
    @staticmethod
    def validate_caller_physical_id(value: str) -> Tuple[bool, Optional[str]]:
        """
        验证物理主叫 ID
        
        Args:
            value: 物理主叫 ID 字符串
        
        Returns:
            (是否有效，错误信息)
        """
        if not value:
            return False, "Caller physical ID cannot be empty"
        
        pattern = r'^user_[a-zA-Z0-9]+$'
        if not re.match(pattern, value):
            return False, (
                f"Invalid caller_physical_id format: {value}. "
                "Must be user_{id}."
            )
        
        return True, None
    
    @staticmethod
    def validate_called_id(value: str) -> Tuple[bool, Optional[str]]:
        """
        验证被叫 ID
        
        Args:
            value: 被叫 ID 字符串
        
        Returns:
            (是否有效，错误信息)
        """
        if not value:
            return False, "Called ID cannot be empty"
        
        pattern1 = r'^[0-9]{3,4}-[0-9]{3,4}$'
        pattern2 = r'^[a-z][a-z0-9_]*$'
        if not (re.match(pattern1, value) or re.match(pattern2, value)):
            return False, (
                f"Invalid called_id format: {value}. "
                "Must be {prefix}-{number} (e.g., 400-001) or {uuid}."
            )
        
        return True, None
    
    @staticmethod
    def validate_session_id(value: str) -> Tuple[bool, Optional[str]]:
        """
        验证会话 ID
        
        Args:
            value: 会话 ID 字符串
        
        Returns:
            (是否有效，错误信息)
        """
        if not value:
            return False, "Session ID cannot be empty"
        
        pattern = r'^[a-zA-Z0-9_-]+$'
        if not re.match(pattern, value):
            return False, (
                f"Invalid session_id format: {value}. "
                "Must be alphanumeric with underscores and hyphens."
            )
        
        return True, None
    
    @staticmethod
    def validate_message_id(value: str) -> Tuple[bool, Optional[str]]:
        """
        验证消息 ID
        
        Args:
            value: 消息 ID 字符串
        
        Returns:
            (是否有效，错误信息)
        """
        if not value:
            return False, "Message ID cannot be empty"
        
        pattern = r'^[a-zA-Z0-9_-]+$'
        if not re.match(pattern, value):
            return False, (
                f"Invalid message_id format: {value}. "
                "Must be alphanumeric with underscores and hyphens."
            )
        
        return True, None
    
    @staticmethod
    def validate_identifiers(identifiers: Identifiers) -> Tuple[bool, Optional[str]]:
        """
        验证完整的六层标识符集合
        
        Args:
            identifiers: Identifiers 对象
        
        Returns:
            (是否有效，错误信息)
        """
        # 验证每个标识符
        validators = [
            (identifiers.channel_id.value, IdentifierValidator.validate_channel_id),
            (identifiers.caller_logical_id.value, IdentifierValidator.validate_caller_logical_id),
            (identifiers.caller_physical_id.value, IdentifierValidator.validate_caller_physical_id),
            (identifiers.called_id.value, IdentifierValidator.validate_called_id),
            (identifiers.session_id.value, IdentifierValidator.validate_session_id),
            (identifiers.message_id.value, IdentifierValidator.validate_message_id),
        ]
        
        for value, validator in validators:
            valid, error = validator(value)
            if not valid:
                return False, error
        
        # 验证会话类型一致性
        if identifiers.caller_logical_id.is_group:
            if identifiers.channel_type != "group":
                return False, (
                    "caller_logical_id is group but channel_type is not 'group'"
                )
            if identifiers.caller_logical_id.value == identifiers.caller_physical_id.value:
                return False, (
                    "In group chat, caller_logical_id should differ from caller_physical_id"
                )
        else:
            if identifiers.channel_type != "private":
                return False, (
                    "caller_logical_id is user but channel_type is not 'private'"
                )
            if identifiers.caller_logical_id.value != identifiers.caller_physical_id.value:
                return False, (
                    "In private chat, caller_logical_id should equal caller_physical_id"
                )
        
        return True, None
    
    @staticmethod
    def validate_dict(data: dict) -> Tuple[bool, Optional[str]]:
        """
        验证字典格式的标识符
        
        Args:
            data: 包含六层标识符的字典
        
        Returns:
            (是否有效，错误信息)
        """
        required_fields = [
            "channel_id",
            "caller_logical_id",
            "caller_physical_id",
            "called_id",
            "session_id",
            "message_id",
        ]
        
        # 检查必需字段
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        # 验证每个字段
        validators = {
            "channel_id": IdentifierValidator.validate_channel_id,
            "caller_logical_id": IdentifierValidator.validate_caller_logical_id,
            "caller_physical_id": IdentifierValidator.validate_caller_physical_id,
            "called_id": IdentifierValidator.validate_called_id,
            "session_id": IdentifierValidator.validate_session_id,
            "message_id": IdentifierValidator.validate_message_id,
        }
        
        for field, validator in validators.items():
            valid, error = validator(data[field])
            if not valid:
                return False, f"Invalid {field}: {error}"
        
        # 验证会话类型一致性
        channel_type = data.get("channel_type", "private")
        caller_logical_id = data["caller_logical_id"]
        caller_physical_id = data["caller_physical_id"]
        
        if caller_logical_id.startswith("group_"):
            if channel_type != "group":
                return False, "Group caller_logical_id requires channel_type='group'"
            if caller_logical_id == caller_physical_id:
                return False, "In group chat, caller_logical_id should differ from caller_physical_id"
        else:
            if channel_type != "private":
                return False, "User caller_logical_id requires channel_type='private'"
            if caller_logical_id != caller_physical_id:
                return False, "In private chat, caller_logical_id should equal caller_physical_id"
        
        return True, None
    
    @staticmethod
    def assert_valid(identifiers: Identifiers):
        """
        断言标识符有效，否则抛出异常
        
        Args:
            identifiers: Identifiers 对象
        
        Raises:
            ValidationError: 如果标识符无效
        """
        valid, error = IdentifierValidator.validate_identifiers(identifiers)
        if not valid:
            raise ValidationError(error)
    
    @staticmethod
    def assert_valid_dict(data: dict):
        """
        断言字典格式标识符有效，否则抛出异常
        
        Args:
            data: 包含六层标识符的字典
        
        Raises:
            ValidationError: 如果标识符无效
        """
        valid, error = IdentifierValidator.validate_dict(data)
        if not valid:
            raise ValidationError(error)
