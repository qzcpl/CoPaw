"""
BusMessage v3 单元测试

测试消息数据结构、序列化、转换
"""

import pytest
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加补丁目录到路径
patch_src = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(patch_src))

from copaw.app.channels.schema import (
    BusMessage,
    BusMessageV3,
    SessionContext,
    UserProfile,
    GroupContext,
    MessageType,
    MessageStatus,
)
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


class TestBusMessageV3Creation:
    """BusMessage v3 创建测试"""
    
    def test_create_basic_message(self):
        """测试创建基础消息"""
        msg = BusMessageV3(
            message_id="msg_001",
            channel_id="dingtalk",
            caller_id="user_001",
            called_id="400-001",
            session_id="sess_001",
            content="你好",
            message_type=MessageType.TEXT,
            timestamp=datetime.now(),
        )
        
        assert msg.message_id == "msg_001"
        assert msg.channel_id == "dingtalk"
        assert msg.caller_id == "user_001"
        assert msg.called_id == "400-001"
        assert msg.content == "你好"
    
    def test_create_message_with_identifiers(self):
        """测试使用六层标识符创建消息"""
        identifiers = Identifiers(
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
        
        msg = BusMessageV3(
            message_id=identifiers.message_id.value,
            channel_id=identifiers.channel_id.value,
            caller_id=identifiers.caller_logical_id.value,
            called_id=identifiers.called_id.value,
            session_id=identifiers.session_id.value,
            content="你好",
            message_type=MessageType.TEXT,
            timestamp=datetime.now(),
        )
        
        assert msg.message_id == "msg_001"
        assert msg.channel_id == "dingtalk"
        assert msg.caller_id == "user_001"
    
    def test_create_group_message(self):
        """测试创建群聊消息"""
        identifiers = Identifiers(
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
        
        msg = BusMessageV3(
            message_id=identifiers.message_id.value,
            channel_id=identifiers.channel_id.value,
            caller_id=identifiers.caller_logical_id.value,
            called_id=identifiers.called_id.value,
            session_id=identifiers.session_id.value,
            content="大家好",
            message_type=MessageType.TEXT,
            timestamp=datetime.now(),
            group_id=identifiers.caller_logical_id.value,
            sender_id=identifiers.caller_physical_id.value,
        )
        
        assert msg.group_id == "group_001"
        assert msg.sender_id == "user_001"
        assert msg.is_group_message() is True


class TestBusMessageV3Serialization:
    """BusMessage v3 序列化测试"""
    
    def test_message_to_dict(self):
        """测试消息转字典"""
        msg = BusMessageV3(
            message_id="msg_001",
            channel_id="dingtalk",
            caller_id="user_001",
            called_id="400-001",
            session_id="sess_001",
            content="你好",
            message_type=MessageType.TEXT,
            timestamp=datetime.now(),
        )
        
        data = msg.to_dict()
        
        assert data["message_id"] == "msg_001"
        assert data["channel_id"] == "dingtalk"
        assert data["caller_id"] == "user_001"
        assert data["content"] == "你好"
    
    def test_message_from_dict(self):
        """测试从字典创建消息"""
        data = {
            "message_id": "msg_001",
            "channel_id": "dingtalk",
            "caller_id": "user_001",
            "called_id": "400-001",
            "session_id": "sess_001",
            "content": "你好",
            "message_type": "text",
            "timestamp": datetime.now().isoformat(),
        }
        
        msg = BusMessageV3.from_dict(data)
        
        assert msg.message_id == "msg_001"
        assert msg.content == "你好"
    
    def test_message_to_json(self):
        """测试消息转 JSON"""
        msg = BusMessageV3(
            message_id="msg_001",
            channel_id="dingtalk",
            caller_id="user_001",
            called_id="400-001",
            session_id="sess_001",
            content="你好",
            message_type=MessageType.TEXT,
            timestamp=datetime.now(),
        )
        
        json_str = msg.to_json()
        
        assert isinstance(json_str, str)
        assert "msg_001" in json_str
    
    def test_message_from_json(self):
        """测试从 JSON 创建消息"""
        json_str = json.dumps({
            "message_id": "msg_001",
            "channel_id": "dingtalk",
            "caller_id": "user_001",
            "called_id": "400-001",
            "session_id": "sess_001",
            "content": "你好",
            "message_type": "text",
            "timestamp": datetime.now().isoformat(),
        })
        
        msg = BusMessageV3.from_json(json_str)
        
        assert msg.message_id == "msg_001"
        assert msg.content == "你好"


class TestSessionContext:
    """会话上下文测试"""
    
    def test_create_session_context(self):
        """测试创建会话上下文"""
        ctx = SessionContext(
            channel_id="dingtalk",
            caller_logical_id="user_001",
            caller_physical_id="user_001",
            called_id="400-001",
            session_id="sess_001",
        )
        
        assert ctx.channel_id == "dingtalk"
        assert ctx.caller_logical_id == "user_001"
        assert ctx.called_id == "400-001"
    
    def test_session_context_with_profile(self):
        """测试带用户画像的会话上下文"""
        profile = UserProfile(
            user_id="user_001",
            name="陈总",
            role="总经理",
            company="思恒电子商务",
        )
        
        ctx = SessionContext(
            channel_id="dingtalk",
            caller_logical_id="user_001",
            caller_physical_id="user_001",
            called_id="400-001",
            session_id="sess_001",
            user_profile=profile,
        )
        
        assert ctx.user_profile.name == "陈总"
        assert ctx.user_profile.company == "思恒电子商务"
    
    def test_session_context_with_group(self):
        """测试带群聊上下文的会话"""
        group_ctx = GroupContext(
            group_id="group_001",
            group_name="项目组",
            member_count=10,
        )
        
        ctx = SessionContext(
            channel_id="dingtalk",
            caller_logical_id="group_001",
            caller_physical_id="user_001",
            called_id="400-001",
            session_id="sess_001",
            group_context=group_ctx,
        )
        
        assert ctx.group_context.group_name == "项目组"
        assert ctx.is_group_session() is True
    
    def test_session_context_is_group(self):
        """测试判断是否群聊会话"""
        # 私聊
        ctx1 = SessionContext(
            channel_id="dingtalk",
            caller_logical_id="user_001",
            caller_physical_id="user_001",
            called_id="400-001",
            session_id="sess_001",
        )
        assert ctx1.is_group_session() is False
        
        # 群聊
        ctx2 = SessionContext(
            channel_id="dingtalk",
            caller_logical_id="group_001",
            caller_physical_id="user_001",
            called_id="400-001",
            session_id="sess_001",
            group_context=GroupContext(
                group_id="group_001",
                group_name="项目组",
                member_count=10,
            ),
        )
        assert ctx2.is_group_session() is True
    
    def test_session_context_to_dict(self):
        """测试会话上下文转字典"""
        ctx = SessionContext(
            channel_id="dingtalk",
            caller_logical_id="user_001",
            caller_physical_id="user_001",
            called_id="400-001",
            session_id="sess_001",
        )
        
        data = ctx.to_dict()
        
        assert data["channel_id"] == "dingtalk"
        assert data["caller_logical_id"] == "user_001"
        assert data["called_id"] == "400-001"


class TestMessageType:
    """消息类型测试"""
    
    def test_message_type_values(self):
        """测试消息类型枚举值"""
        assert MessageType.TEXT.value == "text"
        assert MessageType.IMAGE.value == "image"
        assert MessageType.VOICE.value == "voice"
        assert MessageType.FILE.value == "file"
        assert MessageType.LINK.value == "link"
    
    def test_message_type_from_string(self):
        """测试从字符串创建消息类型"""
        assert MessageType.from_string("text") == MessageType.TEXT
        assert MessageType.from_string("image") == MessageType.IMAGE
        assert MessageType.from_string("voice") == MessageType.VOICE


class TestMessageStatus:
    """消息状态测试"""
    
    def test_message_status_values(self):
        """测试消息状态枚举值"""
        assert MessageStatus.PENDING.value == "pending"
        assert MessageStatus.PROCESSING.value == "processing"
        assert MessageStatus.SUCCESS.value == "success"
        assert MessageStatus.FAILED.value == "failed"
        assert MessageStatus.TIMEOUT.value == "timeout"
    
    def test_message_status_is_terminal(self):
        """测试判断是否为终态"""
        assert MessageStatus.SUCCESS.is_terminal() is True
        assert MessageStatus.FAILED.is_terminal() is True
        assert MessageStatus.TIMEOUT.is_terminal() is True
        assert MessageStatus.PENDING.is_terminal() is False
        assert MessageStatus.PROCESSING.is_terminal() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
