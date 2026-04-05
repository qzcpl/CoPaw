"""
会话上下文管理器

负责加载和管理会话上下文，实现会话穿透
"""

import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

from .schema import SessionContext, UserProfile, GroupContext
from .user_profile_loader import UserProfileLoader
from .group_context_loader import GroupContextLoader
from .conversation_summarizer import ConversationSummarizer


@dataclass
class ContextCacheEntry:
    """上下文缓存条目"""
    context: SessionContext
    expires_at: datetime
    access_count: int = 0


class SessionContextManager:
    """
    会话上下文管理器
    
    负责加载和管理会话上下文，实现会话穿透
    
    功能：
    1. 懒加载会话上下文（按需加载）
    2. 缓存机制（减少数据库查询）
    3. 降级方案（缓存失效时返回最小上下文）
    4. 并发安全（异步锁）
    """
    
    def __init__(
        self,
        user_profile_loader: Optional[UserProfileLoader] = None,
        group_context_loader: Optional[GroupContextLoader] = None,
        conversation_summarizer: Optional[ConversationSummarizer] = None,
        cache_ttl_seconds: int = 300,  # 5 分钟
        max_cache_size: int = 1000,
    ):
        """
        Args:
            user_profile_loader: 用户画像加载器
            group_context_loader: 群聊上下文加载器
            conversation_summarizer: 对话摘要生成器
            cache_ttl_seconds: 缓存 TTL（秒）
            max_cache_size: 最大缓存条目数
        """
        self.user_profile_loader = user_profile_loader or UserProfileLoader()
        self.group_context_loader = group_context_loader or GroupContextLoader()
        self.conversation_summarizer = conversation_summarizer or ConversationSummarizer()
        
        self.cache_ttl = timedelta(seconds=cache_ttl_seconds)
        self.max_cache_size = max_cache_size
        self._cache: Dict[str, ContextCacheEntry] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
    
    def _get_cache_key(
        self,
        channel_id: str,
        caller_logical_id: str,
        session_id: str,
    ) -> str:
        """生成缓存键"""
        return f"{channel_id}:{caller_logical_id}:{session_id}"
    
    def _get_lock(self, cache_key: str) -> asyncio.Lock:
        """获取异步锁"""
        if cache_key not in self._locks:
            self._locks[cache_key] = asyncio.Lock()
        return self._locks[cache_key]
    
    def _cleanup_cache(self):
        """清理过期缓存"""
        now = datetime.now()
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.expires_at < now
        ]
        for key in expired_keys:
            del self._cache[key]
        
        # LRU 清理（如果超出大小限制）
        if len(self._cache) > self.max_cache_size:
            # 按访问次数和时间排序
            sorted_entries = sorted(
                self._cache.items(),
                key=lambda x: (x[1].access_count, x[1].expires_at),
            )
            # 删除最少访问的 10%
            remove_count = max(1, self.max_cache_size // 10)
            for key, _ in sorted_entries[:remove_count]:
                del self._cache[key]
    
    async def get_context(
        self,
        channel_id: str,
        caller_logical_id: str,
        caller_physical_id: str,
        called_id: str,
        session_id: str,
        channel_type: str = "private",
        group_id: Optional[str] = None,
        load_full: bool = True,
    ) -> SessionContext:
        """
        获取会话上下文
        
        Args:
            channel_id: 频道 ID
            caller_logical_id: 逻辑主叫 ID
            caller_physical_id: 物理主叫 ID
            called_id: 被叫 ID
            session_id: 会话 ID
            channel_type: 会话类型（private/group）
            group_id: 群 ID（群聊场景）
            load_full: 是否加载完整上下文（用户画像、群聊信息等）
        
        Returns:
            SessionContext 对象
        """
        cache_key = self._get_cache_key(channel_id, caller_logical_id, session_id)
        
        # 尝试从缓存获取
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if entry.expires_at > datetime.now():
                entry.access_count += 1
                return entry.context
            else:
                # 缓存过期，删除
                del self._cache[cache_key]
        
        # 获取锁（避免并发加载）
        lock = self._get_lock(cache_key)
        async with lock:
            # 双重检查（避免锁等待期间已加载）
            if cache_key in self._cache:
                entry = self._cache[cache_key]
                if entry.expires_at > datetime.now():
                    entry.access_count += 1
                    return entry.context
            
            # 创建最小上下文
            context = SessionContext(
                channel=channel_id,
                caller_logical_id=caller_logical_id,
                caller_physical_id=caller_physical_id,
                called_id=called_id,
                session_id=session_id,
            )
            
            # 加载完整上下文（如果需要）
            if load_full:
                await self._enrich_context(context, channel_type, group_id)
            
            # 缓存
            self._cache[cache_key] = ContextCacheEntry(
                context=context,
                expires_at=datetime.now() + self.cache_ttl,
                access_count=1,
            )
            
            # 定期清理
            if len(self._cache) % 100 == 0:
                self._cleanup_cache()
            
            return context
    
    async def _enrich_context(
        self,
        context: SessionContext,
        channel_type: str,
        group_id: Optional[str],
    ):
        """
        丰富上下文信息（懒加载）
        
        Args:
            context: 会话上下文
            channel_type: 会话类型
            group_id: 群 ID
        """
        try:
            # 1. 加载用户画像
            user_profile = await self.user_profile_loader.load_profile(
                user_id=context.caller_physical_id,
                channel_id=context.channel,
            )
            if user_profile:
                context.user_profile = user_profile
            
            # 2. 加载群聊上下文（如果是群聊）
            if channel_type == "group" and group_id:
                group_context = await self.group_context_loader.load_context(
                    group_id=group_id,
                    channel_id=context.channel,
                )
                if group_context:
                    context.group_context = group_context
            
            # 3. 生成对话摘要（可选）
            # summary = await self.conversation_sumizer.generate_summary(
            #     session_id=context.session_id,
            #     limit=10,
            # )
            # if summary:
            #     context.conversation_history = summary
        
        except Exception as e:
            # 降级方案：加载失败不影响最小上下文
            print(f"⚠️  Failed to enrich context: {e}")
            # 继续返回最小上下文
    
    async def refresh_context(
        self,
        channel_id: str,
        caller_logical_id: str,
        session_id: str,
    ):
        """
        刷新上下文（强制重新加载）
        
        Args:
            channel_id: 频道 ID
            caller_logical_id: 逻辑主叫 ID
            session_id: 会话 ID
        """
        cache_key = self._get_cache_key(channel_id, caller_logical_id, session_id)
        
        # 删除缓存
        if cache_key in self._cache:
            del self._cache[cache_key]
        
        # 下次 get_context 会重新加载
    
    async def invalidate_session(self, session_id: str):
        """
        使会话失效（关闭会话时调用）
        
        Args:
            session_id: 会话 ID
        """
        # 删除所有包含该 session_id 的缓存
        keys_to_remove = [
            key for key in self._cache.keys()
            if session_id in key
        ]
        for key in keys_to_remove:
            del self._cache[key]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        now = datetime.now()
        valid_entries = [
            entry for entry in self._cache.values()
            if entry.expires_at > now
        ]
        
        return {
            "total_entries": len(self._cache),
            "valid_entries": len(valid_entries),
            "expired_entries": len(self._cache) - len(valid_entries),
            "max_size": self.max_cache_size,
            "cache_ttl_seconds": self.cache_ttl.total_seconds(),
            "total_access_count": sum(e.access_count for e in self._cache.values()),
        }
    
    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        self._locks.clear()
