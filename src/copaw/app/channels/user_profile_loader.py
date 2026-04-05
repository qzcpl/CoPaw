"""
用户画像加载器

负责加载用户画像信息，支持缓存和降级方案
"""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from .schema import UserProfile


@dataclass
class UserProfileCacheEntry:
    """用户画像缓存条目"""
    profile: UserProfile
    expires_at: datetime
    source: str  # "cache" | "database" | "channel_api"


class UserProfileLoader:
    """
    用户画像加载器
    
    负责加载用户画像信息
    
    加载策略：
    1. 缓存优先（减少重复查询）
    2. 数据库查询（主要来源）
    3. 频道 API（备选方案）
    4. 降级方案（返回最小画像）
    """
    
    def __init__(
        self,
        cache_ttl_seconds: int = 600,  # 10 分钟
        max_cache_size: int = 5000,
    ):
        """
        Args:
            cache_ttl_seconds: 缓存 TTL（秒）
            max_cache_size: 最大缓存条目数
        """
        self.cache_ttl = timedelta(seconds=cache_ttl_seconds)
        self.max_cache_size = max_cache_size
        self._cache: Dict[str, UserProfileCacheEntry] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
    
    def _get_cache_key(self, user_id: str, channel_id: str) -> str:
        """生成缓存键"""
        return f"{channel_id}:{user_id}"
    
    def _get_lock(self, cache_key: str) -> asyncio.Lock:
        """获取异步锁"""
        if cache_key not in self._locks:
            self._locks[cache_key] = asyncio.Lock()
        return self._locks[cache_key]
    
    async def load_profile(
        self,
        user_id: str,
        channel_id: str,
        use_cache: bool = True,
    ) -> Optional[UserProfile]:
        """
        加载用户画像
        
        Args:
            user_id: 用户 ID（如 user_001）
            channel_id: 频道 ID（如 dingtalk）
            use_cache: 是否使用缓存
        
        Returns:
            UserProfile 对象，如果加载失败返回 None
        """
        cache_key = self._get_cache_key(user_id, channel_id)
        
        # 尝试从缓存获取
        if use_cache and cache_key in self._cache:
            entry = self._cache[cache_key]
            if entry.expires_at > datetime.now():
                return entry.profile
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
                    return entry.profile
            
            # 加载用户画像
            profile = await self._load_from_source(user_id, channel_id)
            
            # 缓存
            if profile:
                self._cache[cache_key] = UserProfileCacheEntry(
                    profile=profile,
                    expires_at=datetime.now() + self.cache_ttl,
                    source=getattr(profile, '_source', 'unknown'),
                )
                
                # 清理过期缓存
                self._cleanup_cache()
            
            return profile
    
    async def _load_from_source(
        self,
        user_id: str,
        channel_id: str,
    ) -> Optional[UserProfile]:
        """
        从数据源加载用户画像
        
        加载顺序：
        1. 数据库查询
        2. 频道 API
        3. 降级方案
        
        Args:
            user_id: 用户 ID
            channel_id: 频道 ID
        
        Returns:
            UserProfile 对象
        """
        profile = None
        
        try:
            # 1. 尝试从数据库加载
            profile = await self._load_from_database(user_id, channel_id)
            if profile:
                profile._source = "database"
                return profile
        except Exception as e:
            print(f"⚠️  Failed to load profile from database: {e}")
        
        try:
            # 2. 尝试从频道 API 加载
            profile = await self._load_from_channel_api(user_id, channel_id)
            if profile:
                profile._source = "channel_api"
                return profile
        except Exception as e:
            print(f"⚠️  Failed to load profile from channel API: {e}")
        
        # 3. 降级方案：返回最小画像
        return self._create_minimal_profile(user_id, channel_id)
    
    async def _load_from_database(
        self,
        user_id: str,
        channel_id: str,
    ) -> Optional[UserProfile]:
        """
        从数据库加载用户画像
        
        Args:
            user_id: 用户 ID
            channel_id: 频道 ID
        
        Returns:
            UserProfile 对象
        """
        # TODO: 实现数据库查询
        # 示例代码：
        # from copaw.app.database import get_session
        # from copaw.app.database.models import UserRecord
        #
        # with get_session() as session:
        #     record = session.query(UserRecord).filter(
        #         UserRecord.user_id == user_id,
        #         UserRecord.channel_id == channel_id,
        #     ).first()
        #     if record:
        #         return UserProfile(
        #             user_id=record.user_id,
        #             name=record.name,
        #             avatar=record.avatar,
        #             tags=record.tags,
        #             preferences=record.preferences,
        #         )
        
        # 暂时返回 None，触发下一级加载
        return None
    
    async def _load_from_channel_api(
        self,
        user_id: str,
        channel_id: str,
    ) -> Optional[UserProfile]:
        """
        从频道 API 加载用户画像
        
        Args:
            user_id: 用户 ID
            channel_id: 频道 ID
        
        Returns:
            UserProfile 对象
        """
        # TODO: 根据不同频道调用不同的 API
        # 示例代码：
        # if channel_id == "dingtalk":
        #     from copaw.app.channels.dingtalk import get_user_info
        #     info = await get_user_info(user_id)
        #     return UserProfile(
        #         user_id=user_id,
        #         name=info.get("name"),
        #         avatar=info.get("avatar"),
        #     )
        
        # 暂时返回 None，触发降级方案
        return None
    
    def _create_minimal_profile(
        self,
        user_id: str,
        channel_id: str,
    ) -> UserProfile:
        """
        创建最小用户画像（降级方案）
        
        Args:
            user_id: 用户 ID
            channel_id: 频道 ID
        
        Returns:
            最小 UserProfile 对象
        """
        return UserProfile(
            user_id=user_id,
            name=None,  # 未知
            avatar=None,
            tags=[],
            preferences={},
            metadata={
                "channel_id": channel_id,
                "fallback": True,
                "reason": "Profile not found",
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
    
    async def refresh_profile(
        self,
        user_id: str,
        channel_id: str,
    ):
        """
        刷新用户画像（强制重新加载）
        
        Args:
            user_id: 用户 ID
            channel_id: 频道 ID
        """
        cache_key = self._get_cache_key(user_id, channel_id)
        
        # 删除缓存
        if cache_key in self._cache:
            del self._cache[cache_key]
        
        # 重新加载
        await self.load_profile(user_id, channel_id, use_cache=False)
    
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
