"""
标识符单元测试

测试 Identifiers 和各类标识符
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# 添加补丁目录到路径
patch_src = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(patch_src))

from copaw.identifier.schemas import (
    Identifiers,
    ChannelId,
    CallerLogicalId,
    CallerPhysicalId,
    CalledId,
    SessionId,
    MessageId,
    CallerType,
)


class TestIdentifierGenerator:
    """标识符生成器测试"""
    
    def test_create_channel_id(self):
        """测试创建频道标识符"""
        channel = ChannelId("dingtalk")
        
        assert channel.value == "dingtalk"
        assert str(channel) == "dingtalk"
    
    def test_create_caller_logical_user(self):
        """测试创建用户逻辑主叫标识符"""
        caller = CallerLogicalId(
            value="user_001",
            caller_type=CallerType.USER,
        )
        
        assert caller.value == "user_001"
        assert caller.caller_type == CallerType.USER
        assert str(caller) == "user_001"
    
    def test_create_caller_logical_group(self):
        """测试创建群聊逻辑主叫标识符"""
        caller = CallerLogicalId(
            value="group_001",
            caller_type=CallerType.GROUP,
        )
        
        assert caller.value == "group_001"
        assert caller.caller_type == CallerType.GROUP
    
    def test_create_caller_physical(self):
        """测试创建物理主叫标识符"""
        caller = CallerPhysicalId("user_001")
        
        assert caller.value == "user_001"
    
    def test_create_called_id(self):
        """测试创建被叫标识符"""
        called = CalledId("400-001")
        
        assert called.value == "400-001"
    
    def test_create_session_id(self):
        """测试创建会话标识符"""
        session = SessionId("sess_abc123")
        
        assert session.value == "sess_abc123"
    
    def test_create_message_id(self):
        """测试创建消息标识符"""
        message = MessageId("msg_abc123")
        
        assert message.value == "msg_abc123"
    
    def test_create_full_identifiers(self):
        """测试创建完整六层标识符"""
        full_id = Identifiers(
            channel_id=ChannelId("dingtalk"),
            caller_logical_id=CallerLogicalId(
                value="user_001",
                caller_type=CallerType.USER,
            ),
            caller_physical_id=CallerPhysicalId("user_001"),
            called_id=CalledId("400-001"),
            session_id=SessionId("sess_001"),
            message_id=MessageId("msg_001"),
            channel_type="private",
        )
        
        assert full_id.channel_id.value == "dingtalk"
        assert full_id.caller_logical_id.value == "user_001"
        assert full_id.caller_physical_id.value == "user_001"
        assert full_id.called_id.value == "400-001"
        assert full_id.channel_type == "private"
    
    def test_create_group_chat_identifiers(self):
        """测试创建群聊标识符"""
        full_id = Identifiers(
            channel_id=ChannelId("dingtalk"),
            caller_logical_id=CallerLogicalId(
                value="group_001",
                caller_type=CallerType.GROUP,
            ),
            caller_physical_id=CallerPhysicalId("user_001"),
            called_id=CalledId("400-001"),
            session_id=SessionId("sess_001"),
            message_id=MessageId("msg_001"),
            channel_type="group",
        )
        
        assert full_id.caller_logical_id.value == "group_001"
        assert full_id.caller_physical_id.value == "user_001"
        assert full_id.channel_type == "group"


class TestIdentifierValidator:
    """标识符验证器测试"""
    
    def test_validate_channel_id_valid(self):
        """测试验证合法的频道标识符"""
        channel = ChannelId("dingtalk")
        assert channel.value == "dingtalk"
    
    def test_validate_caller_logical_format(self):
        """测试验证逻辑主叫格式"""
        # 合法格式
        caller1 = CallerLogicalId(value="user_001", caller_type=CallerType.USER)
        assert caller1.value == "user_001"
        
        # 合法格式（带下划线）
        caller2 = CallerLogicalId(value="user_sid_456", caller_type=CallerType.USER)
        assert caller2.value == "user_sid_456"
    
    def test_validate_caller_logical_invalid_type(self):
        """测试验证非法的主叫类型"""
        with pytest.raises(ValueError):
            CallerLogicalId(value="invalid_001", caller_type=CallerType.USER)
    
    def test_validate_called_id_format(self):
        """测试验证被叫标识符格式"""
        # 400 格式
        called1 = CalledId("400-001")
        assert called1.value == "400-001"
        
        # agent 格式
        called2 = CalledId("agent_default")
        assert called2.value == "agent_default"
    
    def test_validate_called_id_invalid(self):
        """测试验证非法的被叫标识符"""
        with pytest.raises(ValueError):
            CalledId("")  # 空值
    
    def test_validate_identifiers_consistency(self):
        """测试标识符一致性"""
        # 私聊场景：caller_logical 和 caller_physical 应该一致
        full_id = Identifiers(
            channel_id=ChannelId("dingtalk"),
            caller_logical_id=CallerLogicalId(
                value="user_001",
                caller_type=CallerType.USER,
            ),
            caller_physical_id=CallerPhysicalId("user_001"),
            called_id=CalledId("400-001"),
            session_id=SessionId("sess_001"),
            message_id=MessageId("msg_001"),
            channel_type="private",
        )
        
        # 私聊场景，两者应该相同
        assert full_id.caller_logical_id.value == full_id.caller_physical_id.value
    
    def test_validate_group_chat_consistency(self):
        """测试群聊标识符一致性"""
        # 群聊场景：caller_logical=群 ID, caller_physical=发送者
        full_id = Identifiers(
            channel_id=ChannelId("dingtalk"),
            caller_logical_id=CallerLogicalId(
                value="group_001",
                caller_type=CallerType.GROUP,
            ),
            caller_physical_id=CallerPhysicalId("user_001"),
            called_id=CalledId("400-001"),
            session_id=SessionId("sess_001"),
            message_id=MessageId("msg_001"),
            channel_type="group",
        )
        
        # 群聊场景，两者不同
        assert full_id.caller_logical_id.value != full_id.caller_physical_id.value
        assert full_id.caller_logical_id.caller_type == CallerType.GROUP


class TestIdentifiersSerialization:
    """标识符序列化测试"""
    
    def test_identifiers_to_dict(self):
        """测试标识符转字典"""
        full_id = Identifiers(
            channel_id=ChannelId("dingtalk"),
            caller_logical_id=CallerLogicalId(
                value="user_001",
                caller_type=CallerType.USER,
            ),
            caller_physical_id=CallerPhysicalId("user_001"),
            called_id=CalledId("400-001"),
            session_id=SessionId("sess_001"),
            message_id=MessageId("msg_001"),
            channel_type="private",
        )
        
        data = full_id.to_dict()
        
        assert data["channel_id"] == "dingtalk"
        assert data["caller_logical_id"] == "user_001"
        assert data["caller_physical_id"] == "user_001"
        assert data["called_id"] == "400-001"
        assert data["channel_type"] == "private"
    
    def test_identifiers_from_dict(self):
        """测试从字典创建标识符"""
        data = {
            "channel_id": "dingtalk",
            "caller_logical_id": "user_001",
            "caller_physical_id": "user_001",
            "called_id": "400-001",
            "session_id": "sess_001",
            "message_id": "msg_001",
            "channel_type": "private",
        }
        
        full_id = Identifiers.from_dict(data)
        
        assert full_id.channel_id.value == "dingtalk"
        assert full_id.caller_logical_id.value == "user_001"
        assert full_id.called_id.value == "400-001"
    
    def test_identifiers_str(self):
        """测试标识符字符串表示"""
        full_id = Identifiers(
            channel_id=ChannelId("dingtalk"),
            caller_logical_id=CallerLogicalId(
                value="user_001",
                caller_type=CallerType.USER,
            ),
            caller_physical_id=CallerPhysicalId("user_001"),
            called_id=CalledId("400-001"),
            session_id=SessionId("sess_001"),
            message_id=MessageId("msg_001"),
            channel_type="private",
        )
        
        str_repr = str(full_id)
        
        assert "dingtalk" in str_repr
        assert "user_001" in str_repr
        assert "400-001" in str_repr


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
