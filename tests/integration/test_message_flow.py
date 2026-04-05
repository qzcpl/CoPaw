"""
消息流转集成测试

测试端到端消息处理流程
"""

import pytest
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

# 添加补丁目录到路径
patch_src = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(patch_src))

from copaw.app.channels.schema import (
    BusMessageV3,
    SessionContext,
    UserProfile,
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


class TestMessageFlowPrivate:
    """私聊消息流转测试"""
    
    @pytest.fixture
    def setup_components(self):
        """设置测试组件"""
        # 模拟组件
        registry = Mock()
        queue = Mock()
        router = Mock()
        context_manager = Mock()
        
        # 配置 mock
        registry.bind = Mock(return_value=Mock(success=True))
        registry.query = Mock(return_value=Mock(
            call_id="400-001",
            agent_id="agent-default",
            tenant_id="tenant-abc",
        ))
        
        queue.enqueue = AsyncMock(return_value=True)
        queue.dequeue = AsyncMock()
        
        router.route = Mock(return_value="agent-default")
        
        context_manager.build_context = Mock(return_value=SessionContext(
            channel_id="dingtalk",
            caller_logical_id="user_001",
            caller_physical_id="user_001",
            called_id="400-001",
            session_id="sess_001",
        ))
        
        return {
            'registry': registry,
            'queue': queue,
            'router': router,
            'context_manager': context_manager,
        }
    
    def test_message_flow_complete(self, setup_components):
        """测试完整消息流转"""
        components = setup_components
        registry = components['registry']
        queue = components['queue']
        router = components['router']
        context_manager = components['context_manager']
        
        # 1. 绑定 callId
        bind_result = registry.bind(
            call_id="400-001",
            agent_id="agent-default",
            tenant_id="tenant-abc",
            channel_id="dingtalk",
        )
        assert bind_result.success is True
        
        # 2. 创建消息
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
        
        # 3. 构建会话上下文
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
        ctx = context_manager.build_context(identifiers)
        assert ctx.channel_id == "dingtalk"
        assert ctx.called_id == "400-001"
        
        # 4. 路由消息
        target_agent = router.route(msg, ctx)
        assert target_agent == "agent-default"
        
        # 5. 入队
        asyncio.run(queue.enqueue(msg))
        queue.enqueue.assert_called_once_with(msg)
        
        # 6. 出队验证
        queue.dequeue.return_value = msg
        dequeued = asyncio.run(queue.dequeue())
        assert dequeued.message_id == "msg_001"
    
    def test_message_with_session_context(self, setup_components):
        """测试带会话上下文的消息"""
        components = setup_components
        context_manager = components['context_manager']
        
        # 创建带用户画像的上下文
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
        
        # 验证上下文信息完整
        assert ctx.user_profile.name == "陈总"
        assert ctx.user_profile.company == "思恒电子商务"
        assert ctx.is_group_session() is False


class TestMessageFlowGroup:
    """群聊消息流转测试"""
    
    @pytest.fixture
    def setup_group_components(self):
        """设置群聊测试组件"""
        registry = Mock()
        queue = Mock()
        router = Mock()
        context_manager = Mock()
        
        registry.bind = Mock(return_value=Mock(success=True))
        registry.query = Mock(return_value=Mock(
            call_id="400-001",
            agent_id="agent-default",
            tenant_id="tenant-abc",
        ))
        
        queue.enqueue = AsyncMock(return_value=True)
        queue.dequeue = AsyncMock()
        
        router.route = Mock(return_value="agent-default")
        
        from copaw.app.channels.schema import GroupContext
        context_manager.build_context = Mock(return_value=SessionContext(
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
        ))
        
        return {
            'registry': registry,
            'queue': queue,
            'router': router,
            'context_manager': context_manager,
        }
    
    def test_group_message_flow(self, setup_group_components):
        """测试群聊消息流转"""
        components = setup_group_components
        context_manager = components['context_manager']
        
        # 创建群聊消息
        msg = BusMessageV3(
            message_id="msg_001",
            channel_id="dingtalk",
            caller_id="group_001",
            called_id="400-001",
            session_id="sess_001",
            content="大家好",
            message_type=MessageType.TEXT,
            timestamp=datetime.now(),
            group_id="group_001",
            sender_id="user_001",
        )
        
        # 构建群聊上下文
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
        ctx = context_manager.build_context(identifiers)
        
        # 验证群聊标识
        assert ctx.caller_logical_id == "group_001"
        assert ctx.caller_physical_id == "user_001"
        assert ctx.is_group_session() is True
        assert ctx.group_context.group_name == "项目组"
    
    def test_group_message_identifiers(self, setup_group_components):
        """测试群聊消息标识符"""
        # 验证双层 callerId 设计
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
        
        # 逻辑 caller = 群 ID
        assert identifiers.caller_logical_id.value == "group_001"
        assert identifiers.caller_logical_id.caller_type == CallerType.GROUP
        
        # 物理 caller = 发送者
        assert identifiers.caller_physical_id.value == "user_001"
        
        # 群聊类型
        assert identifiers.channel_type == "group"


class TestCallIdSwitch:
    """携号转网测试"""
    
    @pytest.fixture
    def setup_registry(self):
        """设置注册表"""
        from copaw.app.callid.registry import CallIdRegistry
        return CallIdRegistry()
    
    def test_switch_agent_preserves_session(self, setup_registry):
        """测试切换 Agent 保留会话"""
        registry = setup_registry
        
        # 初始绑定
        registry.bind(
            call_id="400-001",
            agent_id="agent-old",
            tenant_id="tenant-abc",
            channel_id="dingtalk",
            session_id="sess_001",
        )
        
        # 验证初始状态
        binding = registry.query("400-001")
        assert binding.agent_id == "agent-old"
        assert binding.session_id == "sess_001"
        
        # 切换 Agent
        result = registry.switch_agent(
            call_id="400-001",
            new_agent_id="agent-new",
        )
        
        assert result.success is True
        
        # 验证切换后
        binding = registry.query("400-001")
        assert binding.agent_id == "agent-new"
        assert binding.session_id == "sess_001"  # 会话保留
        assert binding.call_id == "400-001"  # callId 不变
    
    def test_switch_agent_message_routing(self, setup_registry):
        """测试切换后消息路由"""
        registry = setup_registry
        
        # 初始绑定
        registry.bind(
            call_id="400-001",
            agent_id="agent-old",
            tenant_id="tenant-abc",
            channel_id="dingtalk",
        )
        
        # 创建消息
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
        
        # 路由到旧 Agent
        binding = registry.query("400-001")
        assert binding.agent_id == "agent-old"
        
        # 切换 Agent
        registry.switch_agent(
            call_id="400-001",
            new_agent_id="agent-new",
        )
        
        # 路由到新 Agent
        binding = registry.query("400-001")
        assert binding.agent_id == "agent-new"


class TestAdapterIntegration:
    """频道适配器集成测试"""
    
    def test_dingtalk_adapter_convert(self):
        """测试钉钉适配器转换"""
        from copaw.app.channels.adapters.dingtalk import DingTalkAdapter
        
        adapter = DingTalkAdapter()
        
        # 模拟钉钉消息
        dingtalk_msg = {
            "msgId": "dt_msg_001",
            "senderId": "user_001",
            "conversationId": "conv_001",
            "text": {"content": "你好"},
            "timestamp": datetime.now().isoformat(),
        }
        
        # 转换为 BusMessage
        bus_msg = adapter.to_bus_message(dingtalk_msg)
        
        assert bus_msg.message_id == "dt_msg_001"
        assert bus_msg.caller_id == "user_001"
        assert bus_msg.content == "你好"
    
    def test_dingtalk_adapter_convert_back(self):
        """测试钉钉适配器反向转换"""
        from copaw.app.channels.adapters.dingtalk import DingTalkAdapter
        
        adapter = DingTalkAdapter()
        
        # 创建 BusMessage
        bus_msg = BusMessageV3(
            message_id="msg_001",
            channel_id="dingtalk",
            caller_id="agent_001",
            called_id="user_001",
            session_id="sess_001",
            content="你好",
            message_type=MessageType.TEXT,
            timestamp=datetime.now(),
        )
        
        # 转换为钉钉消息
        dingtalk_msg = adapter.from_bus_message(bus_msg)
        
        assert dingtalk_msg is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
