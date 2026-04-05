"""
会话穿透管理器单元测试

测试 SessionPenetrationManager 和相关组件
"""

import pytest
import sys
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


class TestSessionPenetrationManager:
    """会话穿透管理器测试"""
    
    @pytest.fixture
    def mock_profile_loader(self):
        """模拟用户画像加载器"""
        loader = Mock()
        loader.load_profile = AsyncMock(return_value=UserProfile(
            user_id="user_001",
            name="陈总",
            role="总经理",
            company="思恒电子商务",
        ))
        return loader
    
    @pytest.fixture
    def mock_group_loader(self):
        """模拟群聊上下文加载器"""
        loader = Mock()
        loader.load_group_context = AsyncMock(return_value=GroupContext(
            group_id="group_001",
            group_name="项目组",
            member_count=10,
        ))
        return loader
    
    @pytest.fixture
    def mock_summarizer(self):
        """模拟对话摘要生成器"""
        summarizer = Mock()
        summarizer.generate_summary = AsyncMock(return_value="最近讨论了项目进度")
        return loader
    
    @pytest.fixture
    def penetration_manager(self, mock_profile_loader, mock_group_loader, mock_summarizer):
        """创建穿透管理器实例"""
        from copaw.app.channels.context_manager import SessionPenetrationManager
        
        manager = SessionPenetrationManager(
            profile_loader=mock_profile_loader,
            group_loader=mock_group_loader,
            summarizer=mock_summarizer,
        )
        return manager
    
    def test_build_session_context_private(self, penetration_manager):
        """测试构建私聊会话上下文"""
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
        
        ctx = penetration_manager.build_context(identifiers)
        
        assert ctx.channel_id == "dingtalk"
        assert ctx.caller_logical_id == "user_001"
        assert ctx.called_id == "400-001"
        assert ctx.is_group_session() is False
    
    def test_build_session_context_group(self, penetration_manager):
        """测试构建群聊会话上下文"""
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
        
        ctx = penetration_manager.build_context(identifiers)
        
        assert ctx.channel_id == "dingtalk"
        assert ctx.caller_logical_id == "group_001"
        assert ctx.caller_physical_id == "user_001"
        assert ctx.is_group_session() is True
    
    @pytest.mark.asyncio
    async def test_enrich_context_with_profile(self, penetration_manager, mock_profile_loader):
        """测试用用户画像丰富上下文"""
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
        
        ctx = await penetration_manager.enrich_context(identifiers)
        
        assert ctx.user_profile is not None
        assert ctx.user_profile.name == "陈总"
        mock_profile_loader.load_profile.assert_called_once_with("user_001")
    
    @pytest.mark.asyncio
    async def test_enrich_context_with_group(self, penetration_manager, mock_group_loader):
        """测试用群聊上下文丰富会话"""
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
        
        ctx = await penetration_manager.enrich_context(identifiers)
        
        assert ctx.group_context is not None
        assert ctx.group_context.group_name == "项目组"
        mock_group_loader.load_group_context.assert_called_once_with("group_001")
    
    def test_extract_identifiers_from_message(self, penetration_manager):
        """测试从消息提取标识符"""
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
        
        identifiers = penetration_manager.extract_identifiers(msg)
        
        assert identifiers.channel_id.value == "dingtalk"
        assert identifiers.caller_logical_id.value == "user_001"
        assert identifiers.called_id.value == "400-001"
        assert identifiers.message_id.value == "msg_001"
    
    def test_extract_identifiers_from_group_message(self, penetration_manager):
        """测试从群聊消息提取标识符"""
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
        
        identifiers = penetration_manager.extract_identifiers(msg)
        
        assert identifiers.channel_id.value == "dingtalk"
        assert identifiers.caller_logical_id.value == "group_001"
        assert identifiers.caller_physical_id.value == "user_001"
        assert identifiers.channel_type == "group"


class TestUserProfileLoader:
    """用户画像加载器测试"""
    
    @pytest.mark.asyncio
    async def test_load_profile_success(self):
        """测试成功加载用户画像"""
        from copaw.app.channels.user_profile_loader import UserProfileLoader
        
        # 模拟配置文件
        profile_data = {
            "user_001": {
                "name": "陈总",
                "role": "总经理",
                "company": "思恒电子商务",
            }
        }
        
        loader = UserProfileLoader(profile_data=profile_data)
        profile = await loader.load_profile("user_001")
        
        assert profile.user_id == "user_001"
        assert profile.name == "陈总"
        assert profile.company == "思恒电子商务"
    
    @pytest.mark.asyncio
    async def test_load_profile_not_found(self):
        """测试用户不存在"""
        from copaw.app.channels.user_profile_loader import UserProfileLoader
        
        loader = UserProfileLoader(profile_data={})
        profile = await loader.load_profile("unknown_user")
        
        assert profile is None


class TestGroupContextLoader:
    """群聊上下文加载器测试"""
    
    @pytest.mark.asyncio
    async def test_load_group_context_success(self):
        """测试成功加载群聊上下文"""
        from copaw.app.channels.group_context_loader import GroupContextLoader
        
        # 模拟群聊数据
        group_data = {
            "group_001": {
                "group_name": "项目组",
                "member_count": 10,
                "description": "项目开发群",
            }
        }
        
        loader = GroupContextLoader(group_data=group_data)
        ctx = await loader.load_group_context("group_001")
        
        assert ctx.group_id == "group_001"
        assert ctx.group_name == "项目组"
        assert ctx.member_count == 10
    
    @pytest.mark.asyncio
    async def test_load_group_context_not_found(self):
        """测试群聊不存在"""
        from copaw.app.channels.group_context_loader import GroupContextLoader
        
        loader = GroupContextLoader(group_data={})
        ctx = await loader.load_group_context("unknown_group")
        
        assert ctx is None


class TestConversationSummarizer:
    """对话摘要生成器测试"""
    
    @pytest.mark.asyncio
    async def test_generate_summary(self):
        """测试生成对话摘要"""
        from copaw.app.channels.conversation_summarizer import ConversationSummarizer
        
        # 模拟历史消息
        history = [
            {"role": "user", "content": "项目进度如何？"},
            {"role": "assistant", "content": "已完成 80%"},
            {"role": "user", "content": "什么时候能上线？"},
        ]
        
        summarizer = ConversationSummarizer()
        summary = await summarizer.generate_summary("sess_001", history)
        
        assert isinstance(summary, str)
        assert len(summary) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
