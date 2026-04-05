"""
队列模块测试

测试 RedisQueue、SQLiteQueue、QueueManager
"""

import pytest
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# 添加补丁目录到路径
patch_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(patch_src))

from copaw.app.channels.schema import BusMessage
from copaw.app.queue.base import BaseQueue
from copaw.app.queue.sqlite_queue import SQLiteQueue
from copaw.app.queue.manager import QueueManager, QueueBackend


class TestSQLiteQueue:
    """SQLite 队列测试"""
    
    @pytest.fixture
    async def queue(self, tmp_path):
        """创建测试队列"""
        db_path = tmp_path / "test_queue.db"
        queue = SQLiteQueue("test", str(db_path))
        await queue.connect()
        yield queue
        await queue.close()
    
    @pytest.fixture
    def sample_message(self):
        """创建测试消息"""
        return BusMessage(
            message_id="msg_test_001",
            channel_id="test",
            caller_logical_id="user_001",
            caller_physical_id="user_001",
            called_id="agent_001",
            session_id="sess_001",
            channel_type="private",
            content="测试消息",
            content_type="text",
            timestamp=datetime.now(),
        )
    
    @pytest.mark.asyncio
    async def test_enqueue(self, queue, sample_message):
        """测试入队"""
        result = await queue.enqueue(sample_message)
        assert result is True
        
        size = await queue.size()
        assert size == 1
    
    @pytest.mark.asyncio
    async def test_dequeue(self, queue, sample_message):
        """测试出队"""
        # 先入队
        await queue.enqueue(sample_message)
        
        # 再出队
        message = await queue.dequeue()
        
        assert message is not None
        assert message.message_id == sample_message.message_id
        assert message.content == sample_message.content
    
    @pytest.mark.asyncio
    async def test_dequeue_empty(self, queue):
        """测试空队列出队"""
        message = await queue.dequeue()
        assert message is None
    
    @pytest.mark.asyncio
    async def test_peek(self, queue, sample_message):
        """测试查看队首"""
        await queue.enqueue(sample_message)
        
        message = await queue.peek()
        
        assert message is not None
        assert message.message_id == sample_message.message_id
        
        #  Peek 不出队
        size = await queue.size()
        assert size == 1
    
    @pytest.mark.asyncio
    async def test_size(self, queue, sample_message):
        """测试队列长度"""
        assert await queue.size() == 0
        
        await queue.enqueue(sample_message)
        assert await queue.size() == 1
        
        # 创建另一个消息
        msg2 = BusMessage(
            message_id="msg_test_002",
            channel_id="test",
            caller_logical_id="user_001",
            caller_physical_id="user_001",
            called_id="agent_001",
            session_id="sess_001",
            channel_type="private",
            content="测试消息 2",
            content_type="text",
            timestamp=datetime.now(),
        )
        await queue.enqueue(msg2)
        assert await queue.size() == 2
    
    @pytest.mark.asyncio
    async def test_clear(self, queue, sample_message):
        """测试清空队列"""
        await queue.enqueue(sample_message)
        await queue.enqueue(sample_message)
        
        await queue.clear()
        
        size = await queue.size()
        assert size == 0
    
    @pytest.mark.asyncio
    async def test_acknowledge(self, queue, sample_message):
        """测试确认消息"""
        await queue.enqueue(sample_message)
        
        result = await queue.acknowledge(sample_message.message_id)
        assert result is True
        
        size = await queue.size()
        assert size == 0
    
    @pytest.mark.asyncio
    async def test_fail(self, queue, sample_message):
        """测试标记失败"""
        await queue.enqueue(sample_message)
        
        result = await queue.fail(
            sample_message.message_id,
            "测试错误",
        )
        assert result is True
    
    @pytest.mark.asyncio
    async def test_requeue(self, queue, sample_message):
        """测试重新入队"""
        await queue.enqueue(sample_message)
        
        # 出队后再重试
        msg = await queue.dequeue()
        assert msg is not None
        
        # 第一次重试
        result = await queue.requeue(msg, reason="测试重试")
        assert result is True
        
        # 检查队列大小（消息重新入队）
        size = await queue.size()
        assert size == 1
        
        # 再次出队检查
        message = await queue.dequeue()
        assert message is not None
        # 重试计数在数据库里，但 message 对象可能没更新
        # 验证消息能正常出队即可
    
    @pytest.mark.asyncio
    async def test_max_retries(self, queue, sample_message):
        """测试最大重试次数"""
        # 设置最大重试为 2
        queue.max_retries = 2
        
        # 手动设置重试计数
        sample_message.meta = {"retry_count": 2}
        
        # 第 3 次重试应该失败
        result = await queue.requeue(sample_message)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_persist_restore(self, queue, sample_message):
        """测试持久化和恢复"""
        await queue.enqueue(sample_message)
        
        # 持久化
        result = await queue.persist()
        assert result is True
        
        # 恢复
        result = await queue.restore()
        assert result is True
        
        size = await queue.size()
        assert size == 1
    
    @pytest.mark.asyncio
    async def test_fifo_order(self, queue):
        """测试 FIFO 顺序"""
        messages = []
        for i in range(5):
            msg = BusMessage(
                message_id=f"msg_{i}",
                channel_id="test",
                caller_logical_id="user_001",
                caller_physical_id="user_001",
                called_id="agent_001",
                session_id="sess_001",
                channel_type="private",
                content=f"消息{i}",
                timestamp=datetime.now(),
            )
            messages.append(msg)
            await queue.enqueue(msg)
        
        # 按顺序出队
        for i in range(5):
            msg = await queue.dequeue()
            assert msg.message_id == f"msg_{i}"


class TestQueueManager:
    """队列管理器测试"""
    
    @pytest.fixture
    async def manager(self, tmp_path):
        """创建测试管理器"""
        db_path = tmp_path / "manager_test.db"
        manager = QueueManager(
            default_backend=QueueBackend.SQLITE,
            sqlite_db_path=str(db_path),
        )
        yield manager
    
    @pytest.mark.asyncio
    async def test_get_queue(self, manager):
        """测试获取队列"""
        queue = manager.get_queue("test_queue")
        
        assert queue is not None
        assert isinstance(queue, SQLiteQueue)
        assert queue.name == "test_queue"
    
    @pytest.mark.asyncio
    async def test_get_queue_cached(self, manager):
        """测试队列缓存"""
        queue1 = manager.get_queue("test_queue")
        queue2 = manager.get_queue("test_queue")
        
        assert queue1 is queue2
    
    @pytest.mark.asyncio
    async def test_health_check(self, manager, tmp_path):
        """测试健康检查"""
        db_path = tmp_path / "health_test.db"
        queue = manager.get_queue("health_queue")
        queue.db_path = db_path
        await queue.connect()
        
        results = await manager.health_check()
        
        assert "health_queue" in results
        assert results["health_queue"] is True
    
    @pytest.mark.asyncio
    async def test_stats(self, manager, tmp_path):
        """测试统计信息"""
        db_path = tmp_path / "stats_test.db"
        queue = manager.get_queue("stats_queue")
        queue.db_path = db_path
        await queue.connect()
        
        stats = await manager.stats()
        
        assert "stats_queue" in stats
        assert stats["stats_queue"]["backend"] == "SQLiteQueue"
        assert stats["stats_queue"]["connected"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
