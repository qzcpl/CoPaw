"""
队列管理器

职责：
1. 管理多个队列实例
2. 支持后端切换（Redis/SQLite）
3. 健康检查
4. 监控统计
"""

import logging
from typing import Optional, Dict
from enum import Enum

from .base import BaseQueue
from .redis_queue import RedisQueue
from .sqlite_queue import SQLiteQueue

logger = logging.getLogger(__name__)


class QueueBackend(str, Enum):
    """队列后端类型"""
    REDIS = "redis"
    SQLITE = "sqlite"


class QueueManager:
    """
    队列管理器
    
    职责：
    1. 管理多个队列实例
    2. 支持后端切换（Redis/SQLite）
    3. 健康检查
    4. 监控统计
    """
    
    def __init__(
        self,
        default_backend: QueueBackend = QueueBackend.REDIS,
        redis_url: str = "redis://localhost:6379",
        sqlite_db_path: str = "data/queue.db",
    ):
        self.default_backend = default_backend
        self.redis_url = redis_url
        self.sqlite_db_path = sqlite_db_path
        
        self._queues: Dict[str, BaseQueue] = {}
        self._connected = False
    
    async def connect(self) -> None:
        """连接所有队列"""
        logger.info("QueueManager connecting...")
        
        # 连接所有已注册的队列
        for name, queue in self._queues.items():
            if hasattr(queue, 'connect'):
                await queue.connect()
        
        self._connected = True
        logger.info("QueueManager connected")
    
    async def close(self) -> None:
        """关闭所有队列"""
        logger.info("QueueManager closing...")
        
        for name, queue in self._queues.items():
            if hasattr(queue, 'close'):
                await queue.close()
        
        self._connected = False
        logger.info("QueueManager closed")
    
    def get_queue(
        self,
        name: str,
        backend: Optional[QueueBackend] = None,
    ) -> BaseQueue:
        """
        获取或创建队列
        
        Args:
            name: 队列名称
            backend: 后端类型（默认使用 default_backend）
        
        Returns:
            队列实例
        """
        if name in self._queues:
            return self._queues[name]
        
        # 创建新队列
        backend = backend or self.default_backend
        
        if backend == QueueBackend.REDIS:
            queue = RedisQueue(name, self.redis_url)
        elif backend == QueueBackend.SQLITE:
            queue = SQLiteQueue(name, self.sqlite_db_path)
        else:
            raise ValueError(f"Unknown backend: {backend}")
        
        self._queues[name] = queue
        logger.info(f"Queue created: {name} ({backend.value})")
        return queue
    
    async def get_queue_size(self, name: str) -> int:
        """获取队列长度"""
        queue = self.get_queue(name)
        return await queue.size()
    
    async def health_check(self) -> Dict[str, bool]:
        """
        健康检查
        
        Returns:
            {队列名：是否健康}
        """
        results = {}
        
        for name, queue in self._queues.items():
            try:
                size = await queue.size()
                results[name] = True
                logger.debug(f"Queue health check: {name} (size={size})")
            except Exception as e:
                results[name] = False
                logger.error(f"Queue health check failed: {name} ({e})")
        
        return results
    
    async def persist_all(self) -> bool:
        """持久化所有队列"""
        success = True
        
        for name, queue in self._queues.items():
            if not await queue.persist():
                success = False
                logger.error(f"Failed to persist queue: {name}")
        
        if success:
            logger.info("All queues persisted")
        
        return success
    
    async def stats(self) -> Dict[str, Dict]:
        """
        获取统计信息
        
        Returns:
            {
                队列名：{
                    size: int,
                    backend: str,
                    connected: bool,
                }
            }
        """
        stats = {}
        
        for name, queue in self._queues.items():
            try:
                size = await queue.size()
                stats[name] = {
                    'size': size,
                    'backend': type(queue).__name__,
                    'connected': True,
                }
            except Exception as e:
                stats[name] = {
                    'size': 0,
                    'backend': type(queue).__name__,
                    'connected': False,
                    'error': str(e),
                }
        
        return stats
    
    async def fallback_to_sqlite(self, failed_queue_name: str) -> BaseQueue:
        """
        故障切换到 SQLite
        
        Args:
            failed_queue_name: 失败的队列名
        
        Returns:
            SQLite 队列实例
        """
        logger.warning(f"Falling back to SQLite for queue: {failed_queue_name}")
        
        # 创建 SQLite 队列
        sqlite_queue = SQLiteQueue(
            f"{failed_queue_name}_fallback",
            self.sqlite_db_path,
        )
        
        # 连接到 SQLite
        await sqlite_queue.connect()
        
        # 替换原队列
        self._queues[failed_queue_name] = sqlite_queue
        
        return sqlite_queue
