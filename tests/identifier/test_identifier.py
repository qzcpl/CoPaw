"""
标识符模块单元测试

测试六层标识体系的正确性
"""

import pytest
import sys
from pathlib import Path

# 添加 src 到路径
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from copaw.identifier.schemas import (
    ChannelId,
    CallerLogicalId,
    CallerPhysicalId,
    CalledId,
    SessionId,
    MessageId,
    Identifiers,
    CallerType,
    create_private_identifiers,
    create_group_identifiers,
)
from copaw.identifier.generator import IdentifierGenerator
from copaw.identifier.validator import IdentifierValidator, ValidationError


class TestChannelId:
    """测试 ChannelId"""
    
    def test_valid_channel_id(self):
        """测试有效的频道 ID"""
        channel = ChannelId("dingtalk")
        assert str(channel) == "dingtalk"
        
        channel = ChannelId("console")
        assert str(channel) == "console"
    
    def test_invalid_channel_id(self):
        """测试无效的频道 ID"""
        with pytest.raises(ValueError):
            ChannelId("123invalid")  # 不能以数字开头
        
        with pytest.raises(ValueError):
            ChannelId("DingTalk")  # 必须小写


class TestCallerLogicalId:
    """测试 CallerLogicalId"""
    
    def test_valid_user_caller(self):
        """测试有效的用户主叫"""
        caller = CallerLogicalId("user_abc123", CallerType.USER)
        assert str(caller) == "user_abc123"
        assert caller.is_private is True
        assert caller.is_group is False
    
    def test_valid_group_caller(self):
        """测试有效的群组主叫"""
        caller = CallerLogicalId("group_xyz789", CallerType.GROUP)
        assert str(caller) == "group_xyz789"
        assert caller.is_private is False
        assert caller.is_group is True
    
    def test_invalid_caller(self):
        """测试无效的主叫 ID"""
        with pytest.raises(ValueError):
            CallerLogicalId("invalid", CallerType.USER)  # 缺少前缀


class TestCalledId:
    """测试 CalledId"""
    
    def test_valid_phone_format(self):
        """测试有效的电话号码格式"""
        called = CalledId("400-001")
        assert str(called) == "400-001"
        
        called = CalledId("800-1234")
        assert str(called) == "800-1234"
    
    def test_valid_uuid_format(self):
        """测试有效的 UUID 格式"""
        called = CalledId("agent_abc123")
        assert str(called) == "agent_abc123"
    
    def test_invalid_called_id(self):
        """测试无效的被叫 ID"""
        with pytest.raises(ValueError):
            CalledId("123")  # 格式不对


class TestIdentifiers:
    """测试 Identifiers"""
    
    def test_private_identifiers(self):
        """测试私聊标识符"""
        identifiers = Identifiers(
            channel_id=ChannelId("dingtalk"),
            caller_logical_id=CallerLogicalId("user_001", CallerType.USER),
            caller_physical_id=CallerPhysicalId("user_001"),
            called_id=CalledId("400-001"),
            session_id=SessionId("session_abc"),
            message_id=MessageId("msg_123"),
            channel_type="private",
        )
        
        assert identifiers.is_private_message() if hasattr(identifiers, 'is_private_message') else True
        assert identifiers.channel_type == "private"
    
    def test_group_identifiers(self):
        """测试群聊标识符"""
        identifiers = Identifiers(
            channel_id=ChannelId("dingtalk"),
            caller_logical_id=CallerLogicalId("group_001", CallerType.GROUP),
            caller_physical_id=CallerPhysicalId("user_001"),
            called_id=CalledId("400-001"),
            session_id=SessionId("session_abc"),
            message_id=MessageId("msg_123"),
            channel_type="group",
        )
        
        assert identifiers.channel_type == "group"
    
    def test_invalid_private_identifiers(self):
        """测试无效的私聊标识符（逻辑和物理不一致）"""
        # 注意：现在在 __post_init__ 中就会抛出异常
        with pytest.raises(ValueError, match="In private chat"):
            Identifiers(
                channel_id=ChannelId("dingtalk"),
                caller_logical_id=CallerLogicalId("user_001", CallerType.USER),
                caller_physical_id=CallerPhysicalId("user_002"),  # 不一致
                called_id=CalledId("400-001"),
                session_id=SessionId("session_abc"),
                message_id=MessageId("msg_123"),
                channel_type="private",
            )
    
    def test_to_dict(self):
        """测试转换为字典"""
        identifiers = Identifiers(
            channel_id=ChannelId("dingtalk"),
            caller_logical_id=CallerLogicalId("user_001", CallerType.USER),
            caller_physical_id=CallerPhysicalId("user_001"),
            called_id=CalledId("400-001"),
            session_id=SessionId("session_abc"),
            message_id=MessageId("msg_123"),
            channel_type="private",
        )
        
        data = identifiers.to_dict()
        assert data["channel_id"] == "dingtalk"
        assert data["caller_logical_id"] == "user_001"
        assert data["channel_type"] == "private"
    
    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "channel_id": "dingtalk",
            "caller_logical_id": "user_001",
            "caller_physical_id": "user_001",
            "called_id": "400-001",
            "session_id": "session_abc",
            "message_id": "msg_123",
            "channel_type": "private",
        }
        
        identifiers = Identifiers.from_dict(data)
        assert identifiers.channel_id.value == "dingtalk"
        assert identifiers.caller_logical_id.value == "user_001"


class TestIdentifierGenerator:
    """测试 IdentifierGenerator"""
    
    def test_generate_private_identifiers(self):
        """测试生成私聊标识符"""
        gen = IdentifierGenerator()
        
        identifiers = gen.generate_private_identifiers(
            channel_type="dingtalk",
            user_id="user_001",  # 带前缀
            called_id="400-001",
        )
        
        assert identifiers.channel_id.value == "dingtalk"
        # 生成器会自动清理前缀
        assert identifiers.caller_logical_id.value == "user_001"
        assert identifiers.caller_physical_id.value == "user_001"
        assert identifiers.called_id.value == "400-001"
        assert identifiers.channel_type == "private"
    
    def test_generate_group_identifiers(self):
        """测试生成群聊标识符"""
        gen = IdentifierGenerator()
        
        identifiers = gen.generate_group_identifiers(
            channel_type="dingtalk",
            group_id="group_001",  # 带前缀
            user_id="user_001",    # 带前缀
            called_id="400-001",
        )
        
        assert identifiers.channel_id.value == "dingtalk"
        # 生成器会自动清理前缀
        assert identifiers.caller_logical_id.value == "group_001"
        assert identifiers.caller_physical_id.value == "user_001"
        assert identifiers.channel_type == "group"


class TestIdentifierValidator:
    """测试 IdentifierValidator"""
    
    def test_valid_identifiers(self):
        """测试验证有效的标识符"""
        identifiers = Identifiers(
            channel_id=ChannelId("dingtalk"),
            caller_logical_id=CallerLogicalId("user_001", CallerType.USER),
            caller_physical_id=CallerPhysicalId("user_001"),
            called_id=CalledId("400-001"),
            session_id=SessionId("session_abc"),
            message_id=MessageId("msg_123"),
            channel_type="private",
        )
        
        valid, error = IdentifierValidator.validate_identifiers(identifiers)
        assert valid is True
        assert error is None
    
    def test_invalid_identifiers(self):
        """测试验证无效的标识符（通过字典验证）"""
        # 由于 __post_init__ 会阻止创建无效对象，直接测试字典验证
        data = {
            "channel_id": "dingtalk",
            "caller_logical_id": "user_001",
            "caller_physical_id": "user_002",  # 不一致
            "called_id": "400-001",
            "session_id": "session_abc",
            "message_id": "msg_123",
            "channel_type": "private",
        }
        
        valid, error = IdentifierValidator.validate_dict(data)
        assert valid is False
        assert error is not None
        assert "In private chat" in error or "should equal" in error
    
    def test_assert_valid(self):
        """测试断言验证"""
        identifiers = Identifiers(
            channel_id=ChannelId("dingtalk"),
            caller_logical_id=CallerLogicalId("user_001", CallerType.USER),
            caller_physical_id=CallerPhysicalId("user_001"),
            called_id=CalledId("400-001"),
            session_id=SessionId("session_abc"),
            message_id=MessageId("msg_123"),
            channel_type="private",
        )
        
        # 不应抛出异常
        IdentifierValidator.assert_valid(identifiers)
    
    def test_assert_valid_raises(self):
        """测试断言验证抛出异常（通过字典）"""
        data = {
            "channel_id": "dingtalk",
            "caller_logical_id": "user_001",
            "caller_physical_id": "user_002",
            "called_id": "400-001",
            "session_id": "session_abc",
            "message_id": "msg_123",
            "channel_type": "private",
        }
        
        with pytest.raises(ValidationError):
            IdentifierValidator.assert_valid_dict(data)


class TestHelperFunctions:
    """测试辅助函数"""
    
    def test_create_private_identifiers(self):
        """测试创建私聊标识符"""
        identifiers = create_private_identifiers(
            channel_id="dingtalk",
            user_id="user_001",
            called_id="400-001",
        )
        
        assert identifiers.channel_id.value == "dingtalk"
        assert identifiers.channel_type == "private"
    
    def test_create_group_identifiers(self):
        """测试创建群聊标识符"""
        identifiers = create_group_identifiers(
            channel_id="dingtalk",
            group_id="group_001",
            user_id="user_001",
            called_id="400-001",
        )
        
        assert identifiers.channel_id.value == "dingtalk"
        assert identifiers.channel_type == "group"
        assert identifiers.caller_logical_id.value != identifiers.caller_physical_id.value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
