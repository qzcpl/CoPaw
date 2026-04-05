"""
对话摘要生成器

负责生成对话历史摘要，帮助 Agent 理解上下文
"""

import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class ConversationSummary:
    """对话摘要"""
    session_id: str
    summary: str
    key_points: List[str]
    generated_at: datetime
    message_count: int
    time_span_minutes: int


class ConversationSummarizer:
    """
    对话摘要生成器
    
    负责生成对话历史摘要
    
    功能：
    1. 提取对话关键点
    2. 生成简洁摘要
    3. 缓存摘要（减少重复生成）
    4. 增量更新（只处理新消息）
    """
    
    def __init__(
        self,
        max_messages: int = 50,  # 最多处理 50 条消息
        summary_max_length: int = 500,  # 摘要最大长度
        cache_ttl_seconds: int = 600,  # 10 分钟
    ):
        """
        Args:
            max_messages: 最多处理的消息数
            summary_max_length: 摘要最大长度（字符）
            cache_ttl_seconds: 缓存 TTL（秒）
        """
        self.max_messages = max_messages
        self.summary_max_length = summary_max_length
        self.cache_ttl = timedelta(seconds=cache_ttl_seconds)
        self._cache: Dict[str, ConversationSummary] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
    
    def _get_cache_key(self, session_id: str) -> str:
        """生成缓存键"""
        return f"summary:{session_id}"
    
    def _get_lock(self, cache_key: str) -> asyncio.Lock:
        """获取异步锁"""
        if cache_key not in self._locks:
            self._locks[cache_key] = asyncio.Lock()
        return self._locks[cache_key]
    
    async def generate_summary(
        self,
        session_id: str,
        messages: Optional[List[Dict[str, Any]]] = None,
        limit: int = 10,
        use_cache: bool = True,
    ) -> Optional[str]:
        """
        生成对话摘要
        
        Args:
            session_id: 会话 ID
            messages: 消息列表（可选，如果为 None 则从数据库加载）
            limit: 最多处理的消息数
            use_cache: 是否使用缓存
        
        Returns:
            摘要字符串
        """
        cache_key = self._get_cache_key(session_id)
        
        # 尝试从缓存获取
        if use_cache and cache_key in self._cache:
            summary = self._cache[cache_key]
            if summary.generated_at + self.cache_ttl > datetime.now():
                return summary.summary
            else:
                # 缓存过期，删除
                del self._cache[cache_key]
        
        # 获取锁
        lock = self._get_lock(cache_key)
        async with lock:
            # 双重检查
            if use_cache and cache_key in self._cache:
                summary = self._cache[cache_key]
                if summary.generated_at + self.cache_ttl > datetime.now():
                    return summary.summary
            
            # 加载消息
            if messages is None:
                messages = await self._load_messages(session_id, limit)
            
            if not messages:
                return None
            
            # 生成摘要
            summary = await self._generate_summary(session_id, messages)
            
            # 缓存
            if summary:
                self._cache[cache_key] = summary
            
            return summary.summary if summary else None
    
    async def _load_messages(
        self,
        session_id: str,
        limit: int,
    ) -> List[Dict[str, Any]]:
        """
        从数据库加载消息
        
        Args:
            session_id: 会话 ID
            limit: 最多加载的消息数
        
        Returns:
            消息列表
        """
        # TODO: 实现数据库查询
        # 示例代码：
        # from copaw.app.database import get_session
        # from copaw.app.database.models import MessageLog
        #
        # with get_session() as session:
        #     messages = session.query(MessageLog).filter(
        #         MessageLog.session_id == session_id,
        #     ).order_by(
        #         MessageLog.created_at.desc()
        #     ).limit(limit).all()
        #     return [msg.to_dict() for msg in messages]
        
        # 暂时返回空列表
        return []
    
    async def _generate_summary(
        self,
        session_id: str,
        messages: List[Dict[str, Any]],
    ) -> Optional[ConversationSummary]:
        """
        生成对话摘要
        
        Args:
            session_id: 会话 ID
            messages: 消息列表
        
        Returns:
            ConversationSummary 对象
        """
        if not messages:
            return None
        
        # 1. 提取关键信息
        participants = set()
        topics = []
        last_message_time = None
        first_message_time = None
        
        for msg in reversed(messages):  # 从旧到新
            participants.add(msg.get("caller_physical_id", "unknown"))
            
            content = msg.get("content", "")
            if content:
                # 简单提取关键词（实际应该用 NLP）
                if len(content) > 10:
                    topics.append(content[:50])
            
            created_at = msg.get("created_at")
            if created_at:
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(created_at)
                if first_message_time is None:
                    first_message_time = created_at
                last_message_time = created_at
        
        # 2. 计算时间跨度
        time_span_minutes = 0
        if first_message_time and last_message_time:
            time_span_minutes = int(
                (last_message_time - first_message_time).total_seconds() / 60
            )
        
        # 3. 生成摘要
        summary_lines = [
            f"对话包含 {len(messages)} 条消息",
            f"参与者：{len(participants)} 人",
            f"时间跨度：{time_span_minutes} 分钟",
        ]
        
        # 添加最近的话题
        if topics:
            recent_topics = topics[-3:]  # 最近 3 个话题
            summary_lines.append(f"最近话题：{' | '.join(recent_topics)}")
        
        summary = "\n".join(summary_lines)
        
        # 限制长度
        if len(summary) > self.summary_max_length:
            summary = summary[:self.summary_max_length] + "..."
        
        return ConversationSummary(
            session_id=session_id,
            summary=summary,
            key_points=topics[-5:],  # 最近 5 个话题
            generated_at=datetime.now(),
            message_count=len(messages),
            time_span_minutes=time_span_minutes,
        )
    
    async def generate_quick_summary(
        self,
        session_id: str,
        message_count: int,
        last_message_content: Optional[str] = None,
    ) -> str:
        """
        生成快速摘要（不加载完整消息）
        
        Args:
            session_id: 会话 ID
            message_count: 消息数量
            last_message_content: 最后一条消息内容
        
        Returns:
            快速摘要字符串
        """
        summary = f"对话包含 {message_count} 条消息"
        
        if last_message_content:
            preview = last_message_content[:100]
            if len(last_message_content) > 100:
                preview += "..."
            summary += f"\n最近：{preview}"
        
        return summary
    
    def invalidate_summary(self, session_id: str):
        """
        使摘要失效（新消息到达时调用）
        
        Args:
            session_id: 会话 ID
        """
        cache_key = self._get_cache_key(session_id)
        if cache_key in self._cache:
            del self._cache[cache_key]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        now = datetime.now()
        valid_entries = [
            entry for entry in self._cache.values()
            if entry.generated_at + self.cache_ttl > now
        ]
        
        return {
            "total_entries": len(self._cache),
            "valid_entries": len(valid_entries),
            "expired_entries": len(self._cache) - len(valid_entries),
            "cache_ttl_seconds": self.cache_ttl.total_seconds(),
        }
    
    def clear_cache(self):
        """清空缓存"""
        self._cache.clear()
        self._locks.clear()
