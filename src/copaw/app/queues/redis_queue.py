"""
Redis 消息队列实现

特性：
- 高性能（内存操作）
- 支持持久化（RDB/AOF）
- 支持发布订阅
- 支持延迟队列

数据结构：
- List: 主队列（FIFO）
- Sorted Set: 延迟队列（按超时时间排序）
- Hash: 消息详情（按 message_id 索引）
"""

import logging
import json
from typing import Optional, List
from datetime import datetime

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from .base import BaseQueue
from copaw.app.channels.schema import BusMessage

logger = logging.getLogger(__name__)


class RedisQueue(BaseQueue):
    """
    Redis 消息队列
    
    特性：
    - 高性能（内存操作）
    - 支持持久化（RDB/AOF）
    - 支持发布订阅
    - 支持延迟队列
    """
    
    def __init__(
        self,
        name: str,
        redis_url: str = "redis://localhost:6379",
        max_retries: int = 3,
    ):
        if not REDIS_AVAILABLE:
            raise ImportError("redis.asyncio is not installed. Run: pip install redis")
        
        super().__init__(name, max_retries)
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        
        # Redis Key 命名
        self.queue_key = f"copaw:queue:{name}"
        self.delay_queue_key = f"copaw:delay_queue:{name}"
        self.message_hash_key = f"copaw:messages:{name}"
    
    async def connect(self) -> None:
        """连接 Redis"""
        self.redis = redis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        logger.info(f"RedisQueue connected: {self.name}")
    
    async def close(self) -> None:
        """关闭连接"""
        if self.redis:
            await self.redis.close()
            logger.info(f"RedisQueue closed: {self.name}")
    
    async def enqueue(self, message: BusMessage) -> bool:
        """
        入队消息
        
        步骤：
        1. 序列化 BusMessage
        2. 存储到消息 Hash（按 message_id 索引）
        3. 推入队列尾部
        """
        try:
            # === 1. 序列化 ===
            message_dict = message.to_dict()
            message_json = json.dumps(message_dict, ensure_ascii=False, default=str)
            
            # === 2. 存储消息详情 ===
            await self.redis.hset(
                self.message_hash_key,
                message.message_id,
                message_json,
            )
            
            # === 3. 推入队列 ===
            await self.redis.rpush(self.queue_key, message.message_id)
            
            logger.debug(f"Message enqueued: {message.message_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to enqueue: {e}")
            return False
    
    async def dequeue(self, timeout: float = 0) -> Optional[BusMessage]:
        """
        出队消息
        
        使用 BLPOP 实现阻塞式出队
        
        Args:
            timeout: 超时时间（秒），0 表示不等待
        """
        try:
            # === 1. 阻塞式出队 ===
            result = await self.redis.blpop(self.queue_key, timeout=timeout)
            
            if not result:
                return None
            
            _, message_id = result
            
            # === 2. 获取消息详情 ===
            message_json = await self.redis.hget(
                self.message_hash_key,
                message_id,
            )
            
            if not message_json:
                logger.warning(f"Message not found: {message_id}")
                return None
            
            # === 3. 反序列化 ===
            message_dict = json.loads(message_json)
            message = BusMessage.from_dict(message_dict)
            
            logger.debug(f"Message dequeued: {message.message_id}")
            return message
        
        except Exception as e:
            logger.error(f"Failed to dequeue: {e}")
            return None
    
    async def peek(self) -> Optional[BusMessage]:
        """查看队首消息"""
        try:
            message_id = await self.redis.lindex(self.queue_key, 0)
            
            if not message_id:
                return None
            
            message_json = await self.redis.hget(
                self.message_hash_key,
                message_id,
            )
            
            if not message_json:
                return None
            
            message_dict = json.loads(message_json)
            return BusMessage.from_dict(message_dict)
        
        except Exception as e:
            logger.error(f"Failed to peek: {e}")
            return None
    
    async def size(self) -> int:
        """队列长度"""
        return await self.redis.llen(self.queue_key)
    
    async def clear(self) -> None:
        """清空队列"""
        await self.redis.delete(self.queue_key)
        await self.redis.delete(self.message_hash_key)
        logger.info(f"Queue cleared: {self.name}")
    
    async def persist(self) -> bool:
        """
        持久化队列
        
        Redis 本身支持 RDB/AOF 持久化，这里触发 BGSAVE
        """
        try:
            await self.redis.bgsave()
            logger.info(f"Redis persistence triggered: {self.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to persist: {e}")
            return False
    
    async def restore(self) -> bool:
        """
        恢复队列
        
        Redis 重启后自动从 RDB/AOF 恢复
        """
        try:
            size = await self.size()
            logger.info(f"Queue restored: {self.name} (size={size})")
            return True
        except Exception as e:
            logger.error(f"Failed to restore: {e}")
            return False
    
    async def acknowledge(self, message_id: str) -> bool:
        """确认消息处理成功"""
        try:
            await self.redis.hdel(self.message_hash_key, message_id)
            logger.debug(f"Message acknowledged: {message_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to acknowledge: {e}")
            return False
    
    async def fail(
        self,
        message_id: str,
        error_message: str,
    ) -> bool:
        """标记消息处理失败"""
        try:
            # 移动到死信队列
            await self.redis.hset(
                f"{self.message_hash_key}:dead",
                message_id,
                json.dumps({"error": error_message}),
            )
            logger.debug(f"Message failed: {message_id}, error={error_message}")
            return True
        except Exception as e:
            logger.error(f"Failed to mark as failed: {e}")
            return False
    
    async def requeue(
        self,
        message: BusMessage,
        reason: str = "",
    ) -> bool:
        """重新入队（失败重试）"""
        # 增加重试计数
        if message.meta is None:
            message.meta = {}
        message.meta["retry_count"] = message.meta.get("retry_count", 0) + 1
        
        if message.meta["retry_count"] > self.max_retries:
            logger.warning(
                f"Message exceeded max retries: {message.message_id}"
            )
            return False
        
        logger.info(
            f"Requeuing message: {message.message_id}, "
            f"retry_count={message.meta['retry_count']}, reason={reason}"
        )
        
        return await self.enqueue(message)
    
    # === 高级功能 ===
    
    async def enqueue_delayed(
        self,
        message: BusMessage,
        delay_seconds: int,
    ) -> bool:
        """
        延迟入队
        
        使用 Sorted Set 实现延迟队列
        """
        try:
            message_dict = message.to_dict()
            message_json = json.dumps(message_dict, ensure_ascii=False, default=str)
            
            # 存储消息详情
            await self.redis.hset(
                self.message_hash_key,
                message.message_id,
                message_json,
            )
            
            # 添加到延迟队列（score=执行时间戳）
            execute_at = datetime.now().timestamp() + delay_seconds
            await self.redis.zadd(
                self.delay_queue_key,
                {message.message_id: execute_at},
            )
            
            logger.debug(
                f"Message delayed: {message.message_id}, "
                f"execute_at={execute_at}"
            )
            return True
        
        except Exception as e:
            logger.error(f"Failed to enqueue delayed: {e}")
            return False
    
    async def process_delay_queue(self) -> int:
        """
        处理延迟队列
        
        将到期的消息移入主队列
        
        Returns:
            处理的消息数
        """
        try:
            now = datetime.now().timestamp()
            
            # 获取到期的消息
            expired = await self.redis.zrangebyscore(
                self.delay_queue_key,
                0,
                now,
            )
            
            if not expired:
                return 0
            
            # 移动到主队列
            for message_id in expired:
                await self.redis.rpush(self.queue_key, message_id)
                await self.redis.zrem(self.delay_queue_key, message_id)
            
            logger.debug(f"Processed {len(expired)} delayed messages")
            return len(expired)
        
        except Exception as e:
            logger.error(f"Failed to process delay queue: {e}")
            return 0
