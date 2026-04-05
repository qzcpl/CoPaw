"""
频道适配器模块单元测试

测试适配器转换、六层标识符、SessionContext 注入
"""

import pytest
import asyncio
from pathlib import Path
import sys
from datetime import datetime

# 添加路径
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
from copaw.app.channels.schema import BusMessage, SessionContext

try:
    from copaw.app.channels.adapters.base import BaseAdapter
    from copaw.app.channels.adapters.dingtalk import DingTalkAdapter
    from copaw.app.channels.adapters.feishu import FeishuAdapter
    from copaw.app.channels.base_v2 import BaseChannelV2
    ADAPTERS_AVAILABLE = True
except ImportError as e:
    print(f"Import error: {e}")
    ADAPTERS_AVAILABLE = False


@pytest.mark.skipif(not ADAPTERS_AVAILABLE, reason="Adapters not available")
class TestDingTalkAdapter:
    """测试钉钉适配器"""
    
    @pytest.mark.asyncio
    async def test_convert_to_bus_message_text(self):
        """测试文本消息转换"""
        adapter = DingTalkAdapter()
        
        # 钉钉文本消息
        raw = {
            "conversationId": "cid_group123",
            "senderId": "sid_user456",
            "senderNick": "张三",
            "robotCode": "robot_001",
            "messageId": "msg_789",
            "createTime": "2026-03-31T10:00:00+08:00",
            "msgtype": "text",
            "text": {
                "content": "你好",
            },
        }
        
        # 转换
        msg = await adapter.convert_to_bus_message(raw)
        
        # 验证六层标识符
        assert msg.channel_id == "dingtalk"
        assert msg.caller_logical_id == "user_sid_user456"
        assert msg.caller_physical_id == "user_sid_user456"
        assert msg.called_id == "robot_001"
        assert msg.session_id.startswith("sess_")
        assert msg.message_id == "msg_789"
        
        # 验证消息内容
        assert msg.content == "你好"
        assert msg.content_type == "text"
        # 注意：适配器只负责转换，session_context 由 BaseChannelV2 注入
        # assert "session_context" in msg.meta
    
    @pytest.mark.asyncio
    async def test_convert_to_bus_message_markdown(self):
        """测试 Markdown 消息转换"""
        adapter = DingTalkAdapter()
        
        raw = {
            "conversationId": "cid_123",
            "senderId": "sid_456",
            "robotCode": "robot_001",
            "messageId": "msg_789",
            "msgtype": "markdown",
            "markdown": {
                "title": "标题",
                "text": "# 你好\n这是 Markdown",
            },
        }
        
        msg = await adapter.convert_to_bus_message(raw)
        
        assert msg.content_type == "markdown"
        assert "# 你好" in msg.content
    
    @pytest.mark.asyncio
    async def test_convert_from_bus_message_text(self):
        """测试 BusMessage → 钉钉消息"""
        adapter = DingTalkAdapter()
        
        msg = BusMessage(
            message_id="msg_001",
            channel_id="dingtalk",
            caller_logical_id="user_123",
            caller_physical_id="user_456",
            called_id="robot_001",
            session_id="sess_789",
            channel_type="private",
            content="你好",
            content_type="text",
            timestamp=datetime.now(),
        )
        
        # 转换
        raw = await adapter.convert_from_bus_message(msg)
        
        # 验证
        assert raw["msgtype"] == "text"
        assert raw["text"]["content"] == "你好"
    
    @pytest.mark.asyncio
    async def test_convert_from_bus_message_markdown(self):
        """测试 BusMessage → 钉钉 Markdown 消息"""
        adapter = DingTalkAdapter()
        
        msg = BusMessage(
            message_id="msg_001",
            channel_id="dingtalk",
            caller_logical_id="user_123",
            caller_physical_id="user_456",
            called_id="robot_001",
            session_id="sess_789",
            channel_type="private",
            content="# 标题\n内容",
            content_type="markdown",
            timestamp=datetime.now(),
        )
        
        raw = await adapter.convert_from_bus_message(msg)
        
        assert raw["msgtype"] == "markdown"
        assert raw["markdown"]["text"] == "# 标题\n内容"
    
    def test_validate_message(self):
        """测试消息验证"""
        adapter = DingTalkAdapter()
        
        # 有效消息
        valid = {
            "conversationId": "cid_123",
            "senderId": "sid_456",
        }
        assert adapter.validate_message(valid) is True
        
        # 无效消息（缺少 conversationId）
        invalid = {
            "senderId": "sid_456",
        }
        assert adapter.validate_message(invalid) is False


@pytest.mark.skipif(not ADAPTERS_AVAILABLE, reason="Adapters not available")
class TestFeishuAdapter:
    """测试飞书适配器"""
    
    @pytest.mark.asyncio
    async def test_convert_to_bus_message_text(self):
        """测试文本消息转换"""
        adapter = FeishuAdapter(config={"app_id": "app_test_001"})
        
        # 飞书文本消息
        raw = {
            "header": {},
            "event": {
                "tenant_key": "tenant_123",
                "message": {
                    "message_id": "msg_789",
                    "chat_id": "chat_456",
                    "message_type": "text",
                    "text": {
                        "content": "你好",
                    },
                    "sender": {
                        "user_id": "ou_user123",
                        "open_id": "ou_user123",
                    },
                    "create_time": "2026-03-31T10:00:00+08:00",
                },
            },
        }
        
        # 转换
        msg = await adapter.convert_to_bus_message(raw)
        
        # 验证六层标识符
        assert msg.channel_id == "feishu"
        assert msg.caller_logical_id == "user_ou_user123"
        assert msg.caller_physical_id == "user_ou_user123"
        assert msg.called_id == "app_test_001"
        assert msg.message_id == "msg_789"
        
        # 验证消息内容
        assert msg.content == "你好"
        assert msg.content_type == "text"
    
    @pytest.mark.asyncio
    async def test_convert_to_bus_message_post(self):
        """测试富文本消息转换"""
        adapter = FeishuAdapter(config={"app_id": "app_test_001"})
        
        raw = {
            "event": {
                "message": {
                    "message_id": "msg_789",
                    "chat_id": "chat_456",
                    "message_type": "post",
                    "content": '{"post":{"zh_cn":{"title":"","content":[[{"tag":"text","text":"你好"}]]}}}',
                    "sender": {"user_id": "ou_123"},
                },
            },
        }
        
        msg = await adapter.convert_to_bus_message(raw)
        
        assert msg.content_type == "post"
        assert "你好" in msg.content
        assert msg.called_id == "app_test_001"
    
    @pytest.mark.asyncio
    async def test_convert_from_bus_message_text(self):
        """测试 BusMessage → 飞书消息"""
        adapter = FeishuAdapter()
        
        msg = BusMessage(
            message_id="msg_001",
            channel_id="feishu",
            caller_logical_id="user_123",
            caller_physical_id="user_456",
            called_id="app_001",
            session_id="sess_789",
            channel_type="private",
            content="你好",
            content_type="text",
            timestamp=datetime.now(),
        )
        
        raw = await adapter.convert_from_bus_message(msg)
        
        assert raw["msg_type"] == "text"
        assert raw["content"]["text"] == "你好"
    
    def test_validate_message(self):
        """测试消息验证"""
        adapter = FeishuAdapter()
        
        # 有效消息
        valid = {
            "event": {
                "message": {
                    "chat_id": "chat_123",
                    "sender": {"user_id": "ou_456"},
                },
            },
        }
        assert adapter.validate_message(valid) is True
        
        # 无效消息（缺少 event）
        invalid = {}
        assert adapter.validate_message(invalid) is False


@pytest.mark.skipif(not ADAPTERS_AVAILABLE, reason="Adapters not available")
class TestBaseChannelV2:
    """测试 BaseChannel v2"""
    
    @pytest.mark.asyncio
    async def test_receive_message(self):
        """测试接收消息"""
        # 创建测试频道
        class TestChannel(BaseChannelV2):
            channel = "test"
            adapter_class = DingTalkAdapter
        
        async def process(msg):
            yield msg
        
        channel = TestChannel(
            process=process,
            adapter_config={"robot_code": "robot_test"},
        )
        
        # 接收消息
        raw = {
            "conversationId": "cid_123",
            "senderId": "sid_456",
            "robotCode": "robot_test",
            "messageId": "msg_789",
            "msgtype": "text",
            "text": {"content": "你好"},
        }
        
        msg = await channel.receive_message(raw)
        
        # 验证
        assert msg is not None
        assert msg.channel_id == "dingtalk"
        assert msg.content == "你好"
        # SessionContext 存储在 meta 中
        assert msg.meta is not None
        assert "session_context" in msg.meta
    
    @pytest.mark.asyncio
    async def test_send_message(self):
        """测试发送消息"""
        class TestChannel(BaseChannelV2):
            channel = "test"
            adapter_class = DingTalkAdapter
        
        async def process(msg):
            yield msg
        
        channel = TestChannel(process=process)
        
        # 创建消息
        msg = BusMessage(
            message_id="msg_001",
            channel_id="dingtalk",
            caller_logical_id="user_123",
            caller_physical_id="user_456",
            called_id="robot_test",
            session_id="sess_789",
            channel_type="private",
            content="你好",
            content_type="text",
            timestamp=datetime.now(),
        )
        
        # 发送
        result = await channel.send_message(msg)
        
        # 验证（默认实现返回 True）
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
