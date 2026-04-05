"""
群聊上下文加载器

负责加载群聊上下文信息，支持缓存和降级方案
"""

import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass

from .schema import GroupContext


@dataclass
class GroupContextCacheEntry:
    """群聊上下文缓存条目"""
    context: GroupContext
    expires_at: datetime
    source: str  # "cache" | "database" | "channel_api"


class GroupContextLoader:
    """
    群聊上下文加载器
    
    负责加载群聊上下文信息
    
    加载策略：
    1. 缓存优先（减少重复查询）
    2. 数据库查询（主要来源）
    3. 频道 API（备选方案）
    4. 降级方案（返回最小上下文）
    """
    
    def __init__(
        self,
        cache_ttl_seconds: int = 300,  # 5 分钟（群聊信息变化较快）
        max_cache_size: int = 2000,
    ):
        """
        Args:
            cache_ttl_seconds: 缓存 TTL（秒）
            max_cache_size: 最大缓存条目数
        """
        self.cache_ttl = timedelta(seconds=cache_ttl_seconds)
        self.max_cache_size = max_cache_size
        self._cache: Dict[str, GroupContextCacheEntry] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
    
    def _get_cache_key(self, group_id: str, channel_id: str) -> str:
        """生成缓存键"""
        return f"{channel_id}:{group_id}"
    
    def _get_lock(self, cache_key: str) -> asyncio.Lock:
        """获取异步锁"""
        if cache_key not in self._locks:
            self._locks[cache_key] = asyncio.Lock()
        return self._locks[cache_key]
    
    async def load_context(
        self,
        group_id: str,
        channel_id: str,
        use_cache: bool = True,
    ) -> Optional[GroupContext]:
        """
        加载群聊上下文
        
        Args:
            group_id: 群 ID
            channel_id: 频道 ID
            use_cache: 是否使用缓存
        
        Returns:
            GroupContext 对象，如果加载失败返回 None
        """
        cache_key = self._get_cache_key(group_id, channel_id)
        
        # 尝试从缓存获取
        if use_cache and cache_key in self._cache:
            entry = self._cache[cache_key]
            if entry.expires_at > datetime.now():
                return entry.context
            else:
                # 缓存过期，删除
                del self._cache[cache_key]
        
        # 获取锁（避免并发加载）
        lock = self._get_lock(cache_key)
        async with lock:
            # 双重检查
            if use_cache and cache_key in self._cache:
                entry = self._cache[cache_key]
                if entry.expires_at > datetime.now():
                    return entry.context
            
            # 加载群聊上下文
            context = await self._load_from_source(group_id, channel_id)
            
            # 缓存
            if context:
                self._cache[cache_key] = GroupContextCacheEntry(
                    context=context,
                    expires_at=datetime.now() + self.cache_ttl,
                    source=getattr(context, '_source', 'unknown'),
                )
                
                # 清理过期缓存
                self._cleanup_cache()
            
            return context
    
    async def _load_from_source(
        self,
        group_id: str,
        channel_id: str,
    ) -> Optional[GroupContext]:
        """
        从数据源加载群聊上下文
        
        加载顺序：
        1. 数据库查询
        2. 频道 API
        3. 降级方案
        
        Args:
            group_id: 群 ID
            channel_id: 频道 ID
        
        Returns:
            GroupContext 对象
        """
        context = None
        
        try:
            # 1. 尝试从数据库加载
            context = await self._load_from_database(group_id, channel_id)
            if context:
                context._source = "database"
                return context
        except Exception as e:
            print(f"⚠️  Failed to load group context from database: {e}")
        
        try:
            # 2. 尝试从频道 API 加载
            context = await self._load_from_channel_api(group_id, channel_id)
            if context:
                context._source = "channel_api"
                return context
        except Exception as e:
            print(f"⚠️  Failed to load group context from channel API: {e}")
        
        # 3. 降级方案：返回最小上下文
        return self._create_minimal_context(group_id, channel_id)
    
    async def _load_from_database(
        self,
        group_id: str,
        channel_id: str,
    ) -> Optional[GroupContext]:
        """
        从数据库加载群聊上下文
        
        Args:
            group_id: 群 ID
            channel_id: 频道 ID
        
        Returns:
            GroupContext 对象
        """
        # TODO: 实现数据库查询
        # 示例代码：
        # from copaw.app.database import get_session
        # from copaw.app.database.models import GroupRecord
        #
        # with get_session() as session:
        #     record = session.query(GroupRecord).filter(
        #         GroupRecord.group_id == group_id,
        #         GroupRecord.channel_id == channel_id,
        #     ).first()
        #     if record:
        #         return GroupContext(
        #             group_id=record.group_id,
        #             group_name=record.group_name,
        #             member_count=record.member_count,
        #             members=record.members,
        #             group_type=record.group_type,
        #         )
        
        # 暂时返回 None，触发下一级加载
        return None
    
    async def _load_from_channel_api(
        self,
        group_id: str,
        channel_id: str,
    ) -> Optional[GroupContext]:
        """
        从频道 API 加载群聊上下文
        
        Args:
            group_id: 群 ID
            channel_id: 频道 ID
        
        Returns:
            GroupContext 对象
        """
        # TODO: 根据不同频道调用不同的 API
        # 示例代码：
        # if channel_id == "dingtalk":
        #     from copaw.app.channels.dingtalk import get_group_info
        #     info = await get_group_info(group_id)
        #     return GroupContext(
        #         group_id=group_id,
        #         group_name=info.get("name"),
        #         member_count=info.get("member_count"),
        #         members=info.get("members", []),
        #     )
        
        # 暂时返回 None，触发降级方案
        return None
    
    def _create_minimal_context(
        self,
        group_id: str,
        channel_id: str,
    ) -> GroupContext:
        """
        创建最小群聊上下文（降级方案）
        
        Args:
            group_id: 群 ID
            channel_id: 频道 ID
        
        Returns:
            最小 GroupContext 对象
        """
        return GroupContext(
            group_id=group_id,
            group_name=None,  # 未知
            member_count=0,
            members=[],
            group_type=None,
            metadata={
                "channel_id": channel_id,
                "fallback": True,
                "reason": "Group context not found",
            },
        )
    
    def _cleanup_cache(self):
        """清理过期缓存"""
        now = datetime.now()
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.expires_at < now
        ]
        for key in expired_keys:
            del self._cache[key]
        
        # LRU 清理
        if len(self._cache) > self.max_cache_size:
            sorted_entries = sorted(
                self._cache.items(),
                key=lambda x: x[1].expires_at,
            )
            remove_count = max(1, self.max_cache_size // 10)
            for key, _ in sorted_entries[:remove_count]:
                del self._cache[key]
    
    async def refresh_context(
        self,
        group_id: str,
        channel_id: str,
    ):
        """
        刷新群聊上下文（强制重新加载）
        
        Args:
            group_id: 群 ID
            channel_id: 频道 ID
        """
        cache_key = self._get_cache_key(group_id, channel_id)
        
        # 删除缓存
        if cache_key in self._cache:
            del self._cache[cache_key]
        
        # 重新加载
        await self.load_context(group_id, channel_id, use_cache=False)
    
    async def update_member_count(
        self,
        group_id: str,
        channel_id: str,
        member_count: int,
    ):
        """
        更新成员数（群成员变化时调用）
        
        Args:
            group_id: 群 ID
            channel_id: 频道 ID
            member_count: 新成员数
        """
        cache_key = self._get_cache_key(group_id, channel_id)
        
        # 更新缓存
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            entry.context.member_count = member_count
            entry.expires_at = datetime.now() + self.cache_ttl
    
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
        }
    
    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        self._locks.clear()
