"""
并发消息处理性能测试

测试消息队列吞吐量、路由性能、会话穿透延迟
"""

import pytest
import sys
import asyncio
import time
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, AsyncMock
import statistics

# 添加补丁目录到路径
patch_src = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(patch_src))

from copaw.app.channels.schema import (
    BusMessageV3,
    MessageType,
)


class TestConcurrentMessageProcessing:
    """并发消息处理测试"""
    
    @pytest.fixture
    def setup_mock_queue(self):
        """设置模拟队列"""
        from copaw.app.queue.memory_queue import MemoryQueue
        
        queue = MemoryQueue("test_perf_queue")
        return queue
    
    @pytest.mark.asyncio
    async def test_enqueue_throughput(self, setup_mock_queue):
        """测试入队吞吐量"""
        queue = setup_mock_queue
        
        # 准备消息
        num_messages = 100
        messages = [
            BusMessageV3(
                message_id=f"msg_{i}",
                channel_id="dingtalk",
                caller_id=f"user_{i % 10}",
                called_id="400-001",
                session_id=f"sess_{i % 10}",
                content=f"消息{i}",
                message_type=MessageType.TEXT,
                timestamp=datetime.now(),
            )
            for i in range(num_messages)
        ]
        
        # 测试入队
        start_time = time.time()
        
        for msg in messages:
            await queue.enqueue(msg)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 计算吞吐量
        qps = num_messages / duration if duration > 0 else float('inf')
        
        print(f"\n入队性能:")
        print(f"  消息数：{num_messages}")
        print(f"  耗时：{duration:.3f}s")
        print(f"  QPS: {qps:.2f}")
        
        # 验证：QPS > 100
        assert qps > 100, f"入队 QPS {qps:.2f} < 100"
    
    @pytest.mark.asyncio
    async def test_dequeue_throughput(self, setup_mock_queue):
        """测试出队吞吐量"""
        queue = setup_mock_queue
        
        # 准备消息
        num_messages = 100
        for i in range(num_messages):
            msg = BusMessageV3(
                message_id=f"msg_{i}",
                channel_id="dingtalk",
                caller_id=f"user_{i % 10}",
                called_id="400-001",
                session_id=f"sess_{i % 10}",
                content=f"消息{i}",
                message_type=MessageType.TEXT,
                timestamp=datetime.now(),
            )
            await queue.enqueue(msg)
        
        # 测试出队
        start_time = time.time()
        
        dequeued_count = 0
        while True:
            msg = await queue.dequeue()
            if msg is None:
                break
            dequeued_count += 1
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 计算吞吐量
        qps = dequeued_count / duration if duration > 0 else float('inf')
        
        print(f"\n出队性能:")
        print(f"  消息数：{dequeued_count}")
        print(f"  耗时：{duration:.3f}s")
        print(f"  QPS: {qps:.2f}")
        
        # 验证：QPS > 100
        assert qps > 100, f"出队 QPS {qps:.2f} < 100"
    
    @pytest.mark.asyncio
    async def test_concurrent_enqueue(self, setup_mock_queue):
        """测试并发入队"""
        queue = setup_mock_queue
        
        # 并发任务
        async def enqueue_batch(batch_id, count):
            for i in range(count):
                msg = BusMessageV3(
                    message_id=f"msg_{batch_id}_{i}",
                    channel_id="dingtalk",
                    caller_id=f"user_{batch_id}",
                    called_id="400-001",
                    session_id=f"sess_{batch_id}",
                    content=f"消息{batch_id}-{i}",
                    message_type=MessageType.TEXT,
                    timestamp=datetime.now(),
                )
                await queue.enqueue(msg)
        
        # 10 个并发任务，每个 10 条消息
        num_tasks = 10
        messages_per_task = 10
        
        start_time = time.time()
        
        tasks = [
            enqueue_batch(i, messages_per_task)
            for i in range(num_tasks)
        ]
        await asyncio.gather(*tasks)
        
        end_time = time.time()
        duration = end_time - start_time
        
        total_messages = num_tasks * messages_per_task
        qps = total_messages / duration if duration > 0 else float('inf')
        
        print(f"\n并发入队性能:")
        print(f"  并发数：{num_tasks}")
        print(f"  总消息数：{total_messages}")
        print(f"  耗时：{duration:.3f}s")
        print(f"  QPS: {qps:.2f}")
        
        # 验证：QPS > 50（并发有锁竞争）
        assert qps > 50, f"并发入队 QPS {qps:.2f} < 50"


class TestRoutingPerformance:
    """路由性能测试"""
    
    @pytest.fixture
    def setup_mock_router(self):
        """设置模拟路由器"""
        from copaw.app.callid.registry import CallIdRegistry
        from copaw.app.router.router import MessageRouter
        
        registry = CallIdRegistry()
        
        # 预绑定一些 callId
        for i in range(100):
            registry.bind(
                call_id=f"400-{i:03d}",
                agent_id=f"agent_{i % 10}",
                tenant_id="tenant-abc",
                channel_id="dingtalk",
            )
        
        router = MessageRouter(registry)
        return router
    
    def test_routing_latency(self, setup_mock_router):
        """测试路由延迟"""
        router = setup_mock_router
        
        # 准备消息
        num_messages = 100
        messages = [
            BusMessageV3(
                message_id=f"msg_{i}",
                channel_id="dingtalk",
                caller_id=f"user_{i % 10}",
                called_id=f"400-{i % 100:03d}",
                session_id=f"sess_{i % 10}",
                content=f"消息{i}",
                message_type=MessageType.TEXT,
                timestamp=datetime.now(),
            )
            for i in range(num_messages)
        ]
        
        # 测试路由
        latencies = []
        
        for msg in messages:
            start_time = time.time()
            router.route(msg, None)
            end_time = time.time()
            
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)
        
        # 统计
        avg_latency = statistics.mean(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        p99_latency = sorted(latencies)[int(len(latencies) * 0.99)]
        
        print(f"\n路由性能:")
        print(f"  平均延迟：{avg_latency:.3f}ms")
        print(f"  P95 延迟：{p95_latency:.3f}ms")
        print(f"  P99 延迟：{p99_latency:.3f}ms")
        
        # 验证：平均延迟 < 10ms
        assert avg_latency < 10, f"平均路由延迟 {avg_latency:.3f}ms > 10ms"
    
    def test_routing_qps(self, setup_mock_router):
        """测试路由 QPS"""
        router = setup_mock_router
        
        # 准备消息
        num_messages = 1000
        messages = [
            BusMessageV3(
                message_id=f"msg_{i}",
                channel_id="dingtalk",
                caller_id=f"user_{i % 10}",
                called_id=f"400-{i % 100:03d}",
                session_id=f"sess_{i % 10}",
                content=f"消息{i}",
                message_type=MessageType.TEXT,
                timestamp=datetime.now(),
            )
            for i in range(num_messages)
        ]
        
        # 测试路由
        start_time = time.time()
        
        for msg in messages:
            router.route(msg, None)
        
        end_time = time.time()
        duration = end_time - start_time
        
        qps = num_messages / duration if duration > 0 else float('inf')
        
        print(f"\n路由吞吐量:")
        print(f"  消息数：{num_messages}")
        print(f"  耗时：{duration:.3f}s")
        print(f"  QPS: {qps:.2f}")
        
        # 验证：QPS > 1000
        assert qps > 1000, f"路由 QPS {qps:.2f} < 1000"


class TestSessionPenetrationPerformance:
    """会话穿透性能测试"""
    
    @pytest.fixture
    def setup_mock_penetration(self):
        """设置模拟穿透组件"""
        from copaw.app.channels.context_manager import SessionPenetrationManager
        from copaw.app.channels.user_profile_loader import UserProfileLoader
        
        # 模拟用户画像数据
        profile_data = {
            f"user_{i}": {
                "name": f"用户{i}",
                "role": "员工",
                "company": "测试公司",
            }
            for i in range(100)
        }
        
        profile_loader = UserProfileLoader(profile_data=profile_data)
        
        manager = SessionPenetrationManager(
            profile_loader=profile_loader,
            group_loader=None,
        )
        
        return manager
    
    @pytest.mark.asyncio
    async def test_context_build_latency(self, setup_mock_penetration):
        """测试上下文构建延迟"""
        manager = setup_mock_penetration
        
        from copaw.identifier.schemas import (
            Identifiers, ChannelId, CallerLogicalId,
            CallerPhysicalId, CalledId, SessionId, MessageId, CallerType,
        )
        
        # 测试多次构建
        latencies = []
        
        for i in range(100):
            identifiers = Identifiers(
                channel_id=ChannelId("dingtalk"),
                caller_logical_id=CallerLogicalId(
                    value=f"user_{i % 100}",
                    caller_type=CallerType.USER,
                ),
                caller_physical_id=CallerPhysicalId(f"user_{i % 100}"),
                called_id=CalledId("400-001"),
                session_id=SessionId(f"sess_{i % 10}"),
                message_id=MessageId(f"msg_{i}"),
                channel_type="private",
            )
            
            start_time = time.time()
            manager.build_context(identifiers)
            end_time = time.time()
            
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)
        
        # 统计
        avg_latency = statistics.mean(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        
        print(f"\n上下文构建性能:")
        print(f"  平均延迟：{avg_latency:.3f}ms")
        print(f"  P95 延迟：{p95_latency:.3f}ms")
        
        # 验证：平均延迟 < 5ms（无异步加载）
        assert avg_latency < 5, f"平均构建延迟 {avg_latency:.3f}ms > 5ms"


class TestStressTest:
    """压力测试"""
    
    @pytest.mark.asyncio
    async def test_sustained_load(self):
        """测试持续高负载"""
        from copaw.app.queue.memory_queue import MemoryQueue
        
        queue = MemoryQueue("test_stress_queue")
        
        # 持续 10 秒高负载
        duration_seconds = 10
        target_qps = 100
        
        start_time = time.time()
        message_count = 0
        
        while time.time() - start_time < duration_seconds:
            # 入队
            msg = BusMessageV3(
                message_id=f"msg_{message_count}",
                channel_id="dingtalk",
                caller_id="user_001",
                called_id="400-001",
                session_id="sess_001",
                content=f"消息{message_count}",
                message_type=MessageType.TEXT,
                timestamp=datetime.now(),
            )
            await queue.enqueue(msg)
            message_count += 1
            
            # 出队
            await queue.dequeue()
            
            # 控制节奏
            await asyncio.sleep(1 / target_qps)
        
        actual_duration = time.time() - start_time
        actual_qps = message_count / actual_duration
        
        print(f"\n压力测试:")
        print(f"  持续时间：{actual_duration:.1f}s")
        print(f"  处理消息数：{message_count}")
        print(f"  实际 QPS: {actual_qps:.2f}")
        
        # 验证：无错误完成
        assert message_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
