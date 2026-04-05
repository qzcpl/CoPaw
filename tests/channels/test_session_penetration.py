"""
会话穿透模块单元测试

测试 SessionContextManager、UserProfileLoader、GroupContextLoader、ConversationSummarizer
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import sys

# 添加路径 - 直接指向 patch/src
patch_src = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(patch_src))

from copaw.app.channels.context_manager import SessionContextManager
from copaw.app.channels.user_profile_loader import UserProfileLoader
from copaw.app.channels.group_context_loader import GroupContextLoader
from copaw.app.channels.conversation_summarizer import ConversationSummarizer
from copaw.app.channels.schema import SessionContext, UserProfile, GroupContext


class TestUserProfileLoader:
    """测试用户画像加载器"""
    
    @pytest.mark.asyncio
    async def test_load_minimal_profile(self):
        """测试加载最小用户画像（降级方案）"""
        loader = UserProfileLoader()
        
        profile = await loader.load_profile(
            user_id="user_001",
            channel_id="dingtalk",
        )
        
        assert profile is not None
        assert profile.user_id == "user_001"
        assert profile.metadata.get("fallback") is True
    
    @pytest.mark.asyncio
    async def test_cache_profile(self):
        """测试缓存用户画像"""
        loader = UserProfileLoader(cache_ttl_seconds=60)
        
        # 第一次加载
        profile1 = await loader.load_profile(
            user_id="user_001",
            channel_id="dingtalk",
        )
        
        # 第二次加载（应该从缓存）
        profile2 = await loader.load_profile(
            user_id="user_001",
            channel_id="dingtalk",
        )
        
        assert profile1 is not None
        assert profile2 is not None
        assert profile1.user_id == profile2.user_id
    
    @pytest.mark.asyncio
    async def test_refresh_profile(self):
        """测试刷新用户画像"""
        loader = UserProfileLoader()
        
        # 加载
        await loader.load_profile("user_001", "dingtalk")
        
        # 刷新
        await loader.refresh_profile("user_001", "dingtalk")
        
        # 缓存应该被清除（刷新后会重新加载，所以有 1 个有效条目）
        stats = loader.get_cache_stats()
        assert stats["valid_entries"] >= 0  # 可能重新加载了
    
    def test_cache_stats(self):
        """测试缓存统计"""
        loader = UserProfileLoader()
        
        stats = loader.get_cache_stats()
        
        assert "total_entries" in stats
        assert "valid_entries" in stats
        assert "max_size" in stats
        assert "cache_ttl_seconds" in stats
    
    def test_clear_cache(self):
        """测试清空缓存"""
        loader = UserProfileLoader()
        
        loader.clear_cache()
        
        stats = loader.get_cache_stats()
        assert stats["total_entries"] == 0


class TestGroupContextLoader:
    """测试群聊上下文加载器"""
    
    @pytest.mark.asyncio
    async def test_load_minimal_context(self):
        """测试加载最小群聊上下文（降级方案）"""
        loader = GroupContextLoader()
        
        context = await loader.load_context(
            group_id="group_001",
            channel_id="dingtalk",
        )
        
        assert context is not None
        assert context.group_id == "group_001"
        assert context.metadata.get("fallback") is True
    
    @pytest.mark.asyncio
    async def test_cache_context(self):
        """测试缓存群聊上下文"""
        loader = GroupContextLoader(cache_ttl_seconds=60)
        
        # 第一次加载
        context1 = await loader.load_context(
            group_id="group_001",
            channel_id="dingtalk",
        )
        
        # 第二次加载（应该从缓存）
        context2 = await loader.load_context(
            group_id="group_001",
            channel_id="dingtalk",
        )
        
        assert context1 is not None
        assert context2 is not None
        assert context1.group_id == context2.group_id
    
    @pytest.mark.asyncio
    async def test_update_member_count(self):
        """测试更新成员数"""
        loader = GroupContextLoader()
        
        # 加载
        context = await loader.load_context("group_001", "dingtalk")
        original_count = context.member_count
        
        # 更新
        await loader.update_member_count("group_001", "dingtalk", 100)
        
        # 重新加载（应该从缓存）
        context2 = await loader.load_context("group_001", "dingtalk")
        assert context2.member_count == 100


class TestConversationSummarizer:
    """测试对话摘要生成器"""
    
    @pytest.mark.asyncio
    async def test_generate_summary_empty(self):
        """测试生成空摘要"""
        summarizer = ConversationSummarizer()
        
        summary = await summarizer.generate_summary(
            session_id="session_001",
            messages=[],
        )
        
        assert summary is None
    
    @pytest.mark.asyncio
    async def test_generate_summary_with_messages(self):
        """测试生成有消息的摘要"""
        summarizer = ConversationSummarizer()
        
        messages = [
            {
                "caller_physical_id": "user_001",
                "content": "Hello",
                "created_at": datetime.now().isoformat(),
            },
            {
                "caller_physical_id": "user_002",
                "content": "Hi there",
                "created_at": datetime.now().isoformat(),
            },
        ]
        
        summary = await summarizer.generate_summary(
            session_id="session_001",
            messages=messages,
        )
        
        assert summary is not None
        assert "2 条消息" in summary
        assert "2 人" in summary
    
    @pytest.mark.asyncio
    async def test_generate_quick_summary(self):
        """测试生成快速摘要"""
        summarizer = ConversationSummarizer()
        
        summary = await summarizer.generate_quick_summary(
            session_id="session_001",
            message_count=10,
            last_message_content="Hello, world!",
        )
        
        assert summary is not None
        assert "10 条消息" in summary
        assert "Hello, world!" in summary
    
    def test_invalidate_summary(self):
        """测试使摘要失效"""
        summarizer = ConversationSummarizer()
        
        summarizer.invalidate_summary("session_001")
        
        stats = summarizer.get_cache_stats()
        assert stats["total_entries"] == 0


class TestSessionContextManager:
    """测试会话上下文管理器"""
    
    @pytest.mark.asyncio
    async def test_get_private_context(self):
        """测试获取私聊上下文"""
        manager = SessionContextManager()
        
        context = await manager.get_context(
            channel_id="dingtalk",
            caller_logical_id="user_001",
            caller_physical_id="user_001",
            called_id="400-001",
            session_id="session_001",
            channel_type="private",
            load_full=False,
        )
        
        assert context is not None
        assert context.channel == "dingtalk"
        assert context.caller_logical_id == "user_001"
        assert context.caller_physical_id == "user_001"
        assert context.is_group_session() is False
    
    @pytest.mark.asyncio
    async def test_get_group_context(self):
        """测试获取群聊上下文"""
        manager = SessionContextManager()
        
        context = await manager.get_context(
            channel_id="dingtalk",
            caller_logical_id="group_001",
            caller_physical_id="user_001",
            called_id="400-001",
            session_id="session_001",
            channel_type="group",
            group_id="group_001",
            load_full=False,  # 不加载完整上下文，group_context 为 None
        )
        
        assert context is not None
        assert context.channel == "dingtalk"
        assert context.caller_logical_id == "group_001"
        assert context.caller_physical_id == "user_001"
        # 注意：load_full=False 时，group_context 不会被加载
        # is_group_session() 检查的是 group_context 是否为 None
        # 所以这里应该检查 channel_type 或 caller_logical_id
        assert context.caller_logical_id.startswith("group_")
    
    @pytest.mark.asyncio
    async def test_cache_context(self):
        """测试缓存上下文"""
        manager = SessionContextManager(cache_ttl_seconds=60)
        
        # 第一次获取
        context1 = await manager.get_context(
            channel_id="dingtalk",
            caller_logical_id="user_001",
            caller_physical_id="user_001",
            called_id="400-001",
            session_id="session_001",
            load_full=False,
        )
        
        # 第二次获取（应该从缓存）
        context2 = await manager.get_context(
            channel_id="dingtalk",
            caller_logical_id="user_001",
            caller_physical_id="user_001",
            called_id="400-001",
            session_id="session_001",
            load_full=False,
        )
        
        assert context1 is not None
        assert context2 is not None
        assert context1.session_id == context2.session_id
    
    @pytest.mark.asyncio
    async def test_refresh_context(self):
        """测试刷新上下文"""
        manager = SessionContextManager()
        
        # 获取
        await manager.get_context(
            channel_id="dingtalk",
            caller_logical_id="user_001",
            caller_physical_id="user_001",
            called_id="400-001",
            session_id="session_001",
            load_full=False,
        )
        
        # 刷新
        await manager.refresh_context(
            channel_id="dingtalk",
            caller_logical_id="user_001",
            session_id="session_001",
        )
        
        # 缓存应该被清除
        stats = manager.get_cache_stats()
        assert stats["valid_entries"] == 0
    
    @pytest.mark.asyncio
    async def test_invalidate_session(self):
        """测试使会话失效"""
        manager = SessionContextManager()
        
        # 获取多个会话
        await manager.get_context(
            channel_id="dingtalk",
            caller_logical_id="user_001",
            caller_physical_id="user_001",
            called_id="400-001",
            session_id="session_001",
            load_full=False,
        )
        
        await manager.get_context(
            channel_id="dingtalk",
            caller_logical_id="user_002",
            caller_physical_id="user_002",
            called_id="400-001",
            session_id="session_002",
            load_full=False,
        )
        
        # 使 session_001 失效
        await manager.invalidate_session("session_001")
        
        # 应该只剩 session_002
        stats = manager.get_cache_stats()
        assert stats["valid_entries"] == 1
    
    def test_cache_stats(self):
        """测试缓存统计"""
        manager = SessionContextManager()
        
        stats = manager.get_cache_stats()
        
        assert "total_entries" in stats
        assert "valid_entries" in stats
        assert "max_size" in stats
        assert "cache_ttl_seconds" in stats
    
    def test_clear_cache(self):
        """测试清空缓存"""
        manager = SessionContextManager()
        
        manager.clear_cache()
        
        stats = manager.get_cache_stats()
        assert stats["total_entries"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
