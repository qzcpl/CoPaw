"""
SQLite 消息队列实现

特性：
- 文件存储（无需额外服务）
- 支持事务
- 降级方案（Redis 不可用时）

适用场景：
- 开发环境
- 小型部署
- Redis 故障降级
"""

import logging
import json
from typing import Optional, List
from datetime import datetime
from pathlib import Path

try:
    import aiosqlite
    AIOSQLITE_AVAILABLE = True
except ImportError:
    AIOSQLITE_AVAILABLE = False

from .base import BaseQueue
from copaw.app.channels.schema import BusMessage

logger = logging.getLogger(__name__)


class SQLiteQueue(BaseQueue):
    """
    SQLite 消息队列
    
    特性：
    - 文件存储（无需额外服务）
    - 支持事务
    - 降级方案（Redis 不可用时）
    """
    
    def __init__(
        self,
        name: str,
        db_path: str = "data/queue.db",
        max_retries: int = 3,
    ):
        if not AIOSQLITE_AVAILABLE:
            raise ImportError("aiosqlite is not installed. Run: pip install aiosqlite")
        
        super().__init__(name, max_retries)
        self.db_path = Path(db_path)
        
        # 确保目录存在
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn: Optional[aiosqlite.Connection] = None
    
    async def connect(self) -> None:
        """连接数据库并初始化表"""
        self.conn = await aiosqlite.connect(str(self.db_path))
        await self._init_db()
        logger.info(f"SQLiteQueue connected: {self.name}")
    
    async def close(self) -> None:
        """关闭连接"""
        if self.conn:
            await self.conn.close()
            logger.info(f"SQLiteQueue closed: {self.name}")
    
    async def _init_db(self) -> None:
        """初始化数据库表"""
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE NOT NULL,
                queue_name TEXT NOT NULL,
                message_json TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                retry_count INTEGER DEFAULT 0,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引
        await self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_queue_status 
            ON messages(queue_name, status)
        """)
        
        await self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_message_id 
            ON messages(message_id)
        """)
        
        await self.conn.commit()
    
    async def enqueue(self, message: BusMessage) -> bool:
        """入队消息"""
        try:
            message_dict = message.to_dict()
            message_json = json.dumps(message_dict, ensure_ascii=False, default=str)
            
            retry_count = message.meta.get("retry_count", 0) if message.meta else 0
            
            await self.conn.execute(
                """
                INSERT INTO messages 
                (message_id, queue_name, message_json, status, retry_count)
                VALUES (?, ?, ?, 'pending', ?)
                """,
                (
                    message.message_id,
                    self.name,
                    message_json,
                    retry_count,
                ),
            )
            await self.conn.commit()
            
            logger.debug(f"Message enqueued: {message.message_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to enqueue: {e}")
            await self.conn.rollback()
            return False
    
    async def dequeue(self, timeout: float = 0) -> Optional[BusMessage]:
        """出队消息"""
        try:
            # 获取队首消息
            async with self.conn.execute(
                """
                SELECT message_json FROM messages
                WHERE queue_name = ? AND status = 'pending'
                ORDER BY created_at ASC
                LIMIT 1
                """,
                (self.name,),
            ) as cursor:
                row = await cursor.fetchone()
            
            if not row:
                return None
            
            message_json = row[0]
            message_dict = json.loads(message_json)
            message = BusMessage.from_dict(message_dict)
            
            # 更新状态为 processing
            await self.conn.execute(
                """
                UPDATE messages
                SET status = 'processing', updated_at = CURRENT_TIMESTAMP
                WHERE message_id = ?
                """,
                (message.message_id,),
            )
            await self.conn.commit()
            
            logger.debug(f"Message dequeued: {message.message_id}")
            return message
        
        except Exception as e:
            logger.error(f"Failed to dequeue: {e}")
            return None
    
    async def peek(self) -> Optional[BusMessage]:
        """查看队首消息"""
        try:
            async with self.conn.execute(
                """
                SELECT message_json FROM messages
                WHERE queue_name = ? AND status = 'pending'
                ORDER BY created_at ASC
                LIMIT 1
                """,
                (self.name,),
            ) as cursor:
                row = await cursor.fetchone()
            
            if not row:
                return None
            
            message_json = row[0]
            message_dict = json.loads(message_json)
            return BusMessage.from_dict(message_dict)
        
        except Exception as e:
            logger.error(f"Failed to peek: {e}")
            return None
    
    async def size(self) -> int:
        """队列长度"""
        async with self.conn.execute(
            """
            SELECT COUNT(*) FROM messages
            WHERE queue_name = ? AND status = 'pending'
            """,
            (self.name,),
        ) as cursor:
            row = await cursor.fetchone()
            return row[0]
    
    async def clear(self) -> None:
        """清空队列"""
        await self.conn.execute(
            "DELETE FROM messages WHERE queue_name = ?",
            (self.name,),
        )
        await self.conn.commit()
        logger.info(f"Queue cleared: {self.name}")
    
    async def persist(self) -> bool:
        """持久化（SQLite 本身就是文件存储）"""
        # SQLite 自动持久化
        return True
    
    async def restore(self) -> bool:
        """恢复队列"""
        try:
            size = await self.size()
            logger.info(f"Queue restored: {self.name} (size={size})")
            return True
        except Exception as e:
            logger.error(f"Failed to restore: {e}")
            return False
    
    async def acknowledge(self, message_id: str) -> bool:
        """
        确认消息处理成功
        
        从队列中删除
        """
        try:
            await self.conn.execute(
                "DELETE FROM messages WHERE message_id = ?",
                (message_id,),
            )
            await self.conn.commit()
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
        """
        标记消息处理失败
        
        更新状态和错误信息
        """
        try:
            await self.conn.execute(
                """
                UPDATE messages
                SET status = 'failed',
                    error_message = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE message_id = ?
                """,
                (error_message, message_id),
            )
            await self.conn.commit()
            logger.debug(f"Message failed: {message_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to mark as failed: {e}")
            return False
    
    async def requeue(
        self,
        message: BusMessage,
        reason: str = "",
    ) -> bool:
        """重新入队"""
        # 增加重试计数
        if message.meta is None:
            message.meta = {}
        message.meta["retry_count"] = message.meta.get("retry_count", 0) + 1
        
        if message.meta["retry_count"] > self.max_retries:
            logger.warning(
                f"Message exceeded max retries: {message.message_id}"
            )
            return False
        
        # 更新原消息状态为 pending（而不是插入新消息）
        await self.conn.execute(
            """
            UPDATE messages
            SET status = 'pending',
                retry_count = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE message_id = ?
            """,
            (message.meta["retry_count"], message.message_id),
        )
        await self.conn.commit()
        
        logger.info(
            f"Message requeued: {message.message_id}, "
            f"retry_count={message.meta['retry_count']}"
        )
        return True
    
    async def get_stats(self) -> dict:
        """获取队列统计"""
        async with self.conn.execute(
            """
            SELECT 
                status,
                COUNT(*) as count,
                AVG(retry_count) as avg_retries
            FROM messages
            WHERE queue_name = ?
            GROUP BY status
            """,
            (self.name,),
        ) as cursor:
            rows = await cursor.fetchall()
        
        return {
            row[0]: {"count": row[1], "avg_retries": row[2] or 0}
            for row in rows
        }
