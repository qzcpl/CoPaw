"""
会话穿透集成测试

测试会话上下文构建、用户画像加载、群聊上下文
"""

import pytest
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, AsyncMock

# 添加补丁目录到路径
patch_src = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(patch_src))

from copaw.app.channels.schema import (
    BusMessageV3,
    SessionContext,
    UserProfile,
    GroupContext,
    MessageType,
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


class TestSessionPenetrationIntegration:
    """会话穿透集成测试"""
    
    @pytest.fixture
    def setup_penetration_components(self):
        """设置穿透组件"""
        # 模拟用户画像数据
        profile_data = {
            "user_001": {
                "name": "陈总",
                "role": "总经理",
                "company": "思恒电子商务",
                "preferences": {
                    "timezone": "Asia/Shanghai",
                    "language": "zh-CN",
                },
            },
            "user_002": {
                "name": "李经理",
                "role": "经理",
                "company": "思恒电子商务",
            },
        }
        
        # 模拟群聊数据
        group_data = {
            "group_001": {
                "group_name": "项目组",
                "member_count": 10,
                "description": "项目开发群",
                "admin_ids": ["user_001"],
            },
            "group_002": {
                "group_name": "管理层",
                "member_count": 5,
                "description": "公司管理层",
            },
        }
        
        # 模拟历史对话
        conversation_history = {
            "sess_001": [
                {"role": "user", "content": "项目进度如何？"},
                {"role": "assistant", "content": "已完成 80%"},
                {"role": "user", "content": "什么时候能上线？"},
            ],
            "sess_002": [
                {"role": "user", "content": "下周会议安排"},
                {"role": "assistant", "content": "已为您安排周一上午 10 点"},
            ],
        }
        
        return {
            'profile_data': profile_data,
            'group_data': group_data,
            'conversation_history': conversation_history,
        }
    
    def test_build_complete_session_context(self, setup_penetration_components):
        """测试构建完整会话上下文"""
        from copaw.app.channels.context_manager import SessionPenetrationManager
        from copaw.app.channels.user_profile_loader import UserProfileLoader
        from copaw.app.channels.group_context_loader import GroupContextLoader
        
        profile_loader = UserProfileLoader(
            profile_data=setup_penetration_components['profile_data']
        )
        group_loader = GroupContextLoader(
            group_data=setup_penetration_components['group_data']
        )
        
        manager = SessionPenetrationManager(
            profile_loader=profile_loader,
            group_loader=group_loader,
        )
        
        # 私聊场景
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
        
        ctx = manager.build_context(identifiers)
        
        assert ctx.channel_id == "dingtalk"
        assert ctx.caller_logical_id == "user_001"
        assert ctx.called_id == "400-001"
        assert ctx.is_group_session() is False
    
    @pytest.mark.asyncio
    async def test_enrich_with_user_profile(self, setup_penetration_components):
        """测试用用户画像丰富上下文"""
        from copaw.app.channels.context_manager import SessionPenetrationManager
        from copaw.app.channels.user_profile_loader import UserProfileLoader
        
        profile_loader = UserProfileLoader(
            profile_data=setup_penetration_components['profile_data']
        )
        
        manager = SessionPenetrationManager(
            profile_loader=profile_loader,
            group_loader=None,
        )
        
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
        
        ctx = await manager.enrich_context(identifiers)
        
        assert ctx.user_profile is not None
        assert ctx.user_profile.name == "陈总"
        assert ctx.user_profile.company == "思恒电子商务"
    
    @pytest.mark.asyncio
    async def test_enrich_with_group_context(self, setup_penetration_components):
        """测试用群聊上下文丰富会话"""
        from copaw.app.channels.context_manager import SessionPenetrationManager
        from copaw.app.channels.group_context_loader import GroupContextLoader
        
        group_loader = GroupContextLoader(
            group_data=setup_penetration_components['group_data']
        )
        
        manager = SessionPenetrationManager(
            profile_loader=None,
            group_loader=group_loader,
        )
        
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
        
        ctx = await manager.enrich_context(identifiers)
        
        assert ctx.group_context is not None
        assert ctx.group_context.group_name == "项目组"
        assert ctx.group_context.member_count == 10
        assert ctx.is_group_session() is True
    
    def test_session_context_completeness(self, setup_penetration_components):
        """测试会话上下文完整性"""
        # 构建完整上下文
        profile = UserProfile(
            user_id="user_001",
            name="陈总",
            role="总经理",
            company="思恒电子商务",
        )
        
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
            user_profile=profile,
            group_context=group_ctx,
        )
        
        # 验证所有字段
        assert ctx.channel_id == "dingtalk"
        assert ctx.caller_logical_id == "group_001"
        assert ctx.caller_physical_id == "user_001"
        assert ctx.called_id == "400-001"
        assert ctx.session_id == "sess_001"
        assert ctx.user_profile.name == "陈总"
        assert ctx.group_context.group_name == "项目组"


class TestGroupChatSupport:
    """群聊支持测试"""
    
    def test_group_identifiers_structure(self):
        """测试群聊标识符结构"""
        # 群聊双层 callerId
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
        
        # 频道类型
        assert identifiers.channel_type == "group"
    
    def test_group_message_structure(self):
        """测试群聊消息结构"""
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
        
        # 验证群聊字段
        assert msg.group_id == "group_001"
        assert msg.sender_id == "user_001"
        assert msg.is_group_message() is True
    
    def test_private_vs_group_distinction(self):
        """测试私聊与群聊区分"""
        # 私聊
        private_identifiers = Identifiers(
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
        
        # 群聊
        group_identifiers = Identifiers(
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
        
        # 私聊：caller_logical = caller_physical
        assert private_identifiers.caller_logical_id.value == private_identifiers.caller_physical_id.value
        
        # 群聊：caller_logical != caller_physical
        assert group_identifiers.caller_logical_id.value != group_identifiers.caller_physical_id.value
        
        # 类型不同
        assert private_identifiers.channel_type == "private"
        assert group_identifiers.channel_type == "group"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
