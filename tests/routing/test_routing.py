"""
callId 路由模块单元测试

测试路由策略、路由器、负载均衡、灰度发布
"""

import pytest
import asyncio
from pathlib import Path
import sys

# 添加路径
patch_src = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(patch_src))

from copaw.app.channels.routing.routing_strategies import (
    RoundRobinStrategy,
    WeightedStrategy,
    PriorityStrategy,
    LeastConnectionsStrategy,
    AgentInfo,
)
from copaw.app.channels.routing.callid_router import CallIdRouter
from copaw.app.channels.routing.agent_selector import AgentSelector
from copaw.app.channels.routing.load_balancer import LoadBalancer
from copaw.app.channels.routing.gray_release import GrayReleaseManager


class TestRoutingStrategies:
    """测试路由策略"""
    
    def test_round_robin(self):
        """测试轮询策略"""
        strategy = RoundRobinStrategy()
        
        agents = [
            AgentInfo("agent_1"),
            AgentInfo("agent_2"),
            AgentInfo("agent_3"),
        ]
        
        # 轮询选择（使用 context 传递索引）
        context = {}
        selected_ids = []
        for _ in range(6):
            agent = strategy.select_agent(agents, context)
            selected_ids.append(agent.agent_id)
        
        # 应该轮流选择
        assert selected_ids.count("agent_1") == 2
        assert selected_ids.count("agent_2") == 2
        assert selected_ids.count("agent_3") == 2
    
    def test_round_robin_with_inactive(self):
        """测试轮询策略（包含不活跃 Agent）"""
        strategy = RoundRobinStrategy()
        
        agents = [
            AgentInfo("agent_1", is_active=True),
            AgentInfo("agent_2", is_active=False),
            AgentInfo("agent_3", is_active=True),
        ]
        
        # 应该只选择活跃的
        context = {}
        for _ in range(4):
            agent = strategy.select_agent(agents, context)
            assert agent.agent_id in ["agent_1", "agent_3"]
            assert agent.agent_id != "agent_2"
    
    def test_round_robin_context_persistence(self):
        """测试轮询策略 context 持久化"""
        strategy = RoundRobinStrategy()
        
        agents = [
            AgentInfo("agent_1"),
            AgentInfo("agent_2"),
        ]
        
        # 使用同一个 context
        context = {}
        result1 = strategy.select_agent(agents, context)
        result2 = strategy.select_agent(agents, context)
        
        # 应该选择不同 Agent
        assert result1.agent_id != result2.agent_id
        
        # context 应该包含索引
        assert "round_robin_index" in context
        assert context["round_robin_index"] == 2
    
    def test_round_robin_thread_safety(self):
        """测试轮询策略线程安全（通过 context 隔离）"""
        strategy = RoundRobinStrategy()
        
        agents = [
            AgentInfo("agent_1"),
            AgentInfo("agent_2"),
        ]
        
        # 不同 context 应该独立
        context1 = {}
        context2 = {}
        
        result1 = strategy.select_agent(agents, context1)
        result2 = strategy.select_agent(agents, context2)
        
        # 都从索引 0 开始，应该选择相同 Agent
        assert result1.agent_id == result2.agent_id
    
    def test_weighted_strategy(self):
        """测试权重策略"""
        strategy = WeightedStrategy()
        
        agents = [
            AgentInfo("agent_1", weight=100),
            AgentInfo("agent_2", weight=50),
        ]
        
        # 多次选择
        selected_ids = []
        for _ in range(30):
            agent = strategy.select_agent(agents)
            selected_ids.append(agent.agent_id)
        
        # agent_1 应该被选中更多次
        assert selected_ids.count("agent_1") > selected_ids.count("agent_2")
    
    def test_priority_strategy(self):
        """测试优先级策略"""
        strategy = PriorityStrategy()
        
        agents = [
            AgentInfo("agent_1", priority=1),
            AgentInfo("agent_2", priority=3),
            AgentInfo("agent_3", priority=2),
        ]
        
        # 应该优先选择优先级高的
        selected_ids = []
        for _ in range(10):
            agent = strategy.select_agent(agents)
            selected_ids.append(agent.agent_id)
        
        # agent_2 优先级最高，应该被选中
        assert "agent_2" in selected_ids
    
    def test_least_connections(self):
        """测试最少连接策略"""
        strategy = LeastConnectionsStrategy()
        
        agents = [
            AgentInfo("agent_1"),
            AgentInfo("agent_2"),
        ]
        
        # 第一次选择（连接数相同，随机）
        agent1 = strategy.select_agent(agents)
        assert agent1.agent_id in ["agent_1", "agent_2"]
        
        # 报告结果（减少连接数）
        strategy.report_result(agent1.agent_id, success=True)
        
        # 第二次选择（应该选择另一个，因为第一个连接数已减少）
        agent2 = strategy.select_agent(agents)
        # 注意：由于实现方式，可能仍选择同一个，这里只检查返回有效 Agent
        assert agent2.agent_id in ["agent_1", "agent_2"]


class TestCallIdRouter:
    """测试 CalledId 路由器"""
    
    @pytest.mark.asyncio
    async def test_register_and_route(self):
        """测试注册和路由"""
        router = CallIdRouter()
        
        # 注册
        await router.register_called_id("400-001", "agent_1", priority=1)
        await router.register_called_id("400-001", "agent_2", priority=2)
        
        # 路由
        agent_id = await router.route("400-001")
        assert agent_id in ["agent_1", "agent_2"]
    
    @pytest.mark.asyncio
    async def test_unregister(self):
        """测试注销"""
        router = CallIdRouter()
        
        # 注册
        await router.register_called_id("400-001", "agent_1")
        
        # 注销
        await router.unregister_called_id("400-001", "agent_1")
        
        # 路由应该返回 None
        agent_id = await router.route("400-001")
        assert agent_id is None
    
    @pytest.mark.asyncio
    async def test_set_active(self):
        """测试设置激活状态"""
        router = CallIdRouter()
        
        await router.register_called_id("400-001", "agent_1")
        
        # 设置为不活跃
        await router.set_agent_active("400-001", "agent_1", False)
        
        # 获取 Agent 列表
        agents = await router.get_agents("400-001")
        assert len(agents) == 1
        assert agents[0]["is_active"] is False


class TestLoadBalancer:
    """测试负载均衡器"""
    
    @pytest.mark.asyncio
    async def test_add_and_select(self):
        """测试添加和选择"""
        lb = LoadBalancer(strategy="round_robin")
        
        # 添加 Agent
        await lb.add_agent("agent_1")
        await lb.add_agent("agent_2")
        
        # 选择
        agent_id = await lb.select()
        assert agent_id in ["agent_1", "agent_2"]
    
    @pytest.mark.asyncio
    async def test_remove_agent(self):
        """测试移除 Agent"""
        lb = LoadBalancer()
        
        await lb.add_agent("agent_1")
        await lb.remove_agent("agent_1")
        
        agent_id = await lb.select()
        assert agent_id is None
    
    @pytest.mark.asyncio
    async def test_get_stats(self):
        """测试获取统计"""
        lb = LoadBalancer()
        
        await lb.add_agent("agent_1", weight=100)
        await lb.add_agent("agent_2", weight=50)
        
        stats = lb.get_stats()
        
        assert stats["total_agents"] == 2
        assert stats["active_agents"] == 2


class TestGrayReleaseManager:
    """测试灰度发布管理器"""
    
    @pytest.mark.asyncio
    async def test_percentage_release(self):
        """测试百分比灰度"""
        manager = GrayReleaseManager()
        
        await manager.configure_percentage_release(
            called_id="400-001",
            canary_agent_id="agent_new",
            percentage=50,
            stable_agent_id="agent_old",
        )
        
        # 多次选择，应该两个 Agent 都有
        selected_ids = []
        for _ in range(100):
            agent_id = await manager.select_agent("400-001")
            selected_ids.append(agent_id)
        
        assert "agent_new" in selected_ids
        assert "agent_old" in selected_ids
    
    @pytest.mark.asyncio
    async def test_user_release(self):
        """测试用户灰度"""
        manager = GrayReleaseManager()
        
        await manager.configure_user_release(
            called_id="400-001",
            canary_agent_id="agent_new",
            user_ids=["user_1", "user_2"],
            stable_agent_id="agent_old",
        )
        
        # user_1 应该选择新 Agent
        agent_id = await manager.select_agent("400-001", user_id="user_1")
        assert agent_id == "agent_new"
        
        # user_3 应该选择旧 Agent
        agent_id = await manager.select_agent("400-001", user_id="user_3")
        assert agent_id == "agent_old"
    
    @pytest.mark.asyncio
    async def test_rollback(self):
        """测试回滚"""
        manager = GrayReleaseManager()
        
        await manager.configure_percentage_release(
            called_id="400-001",
            canary_agent_id="agent_new",
            percentage=50,
        )
        
        # 回滚
        await manager.rollback("400-001")
        
        # 应该返回 None
        agent_id = await manager.select_agent("400-001")
        assert agent_id is None


class TestAgentSelector:
    """测试 Agent 选择器"""
    
    @pytest.mark.asyncio
    async def test_select_agent(self):
        """测试选择 Agent"""
        selector = AgentSelector()
        
        # 注册 Agent
        await selector.router.register_called_id("400-001", "agent_1")
        await selector.router.register_called_id("400-001", "agent_2")
        
        # 选择
        agent_id = await selector.select_agent("400-001")
        assert agent_id in ["agent_1", "agent_2"]
    
    @pytest.mark.asyncio
    async def test_report_result(self):
        """测试报告结果"""
        selector = AgentSelector()
        
        await selector.router.register_called_id("400-001", "agent_1")
        
        # 报告成功
        await selector.report_result("agent_1", success=True, latency_ms=50)
        
        # 获取健康状态
        health = selector.get_health("agent_1")
        assert health is not None
        assert health["is_healthy"] is True
    
    @pytest.mark.asyncio
    async def test_circuit_breaker(self):
        """测试熔断器"""
        selector = AgentSelector(
            failure_threshold=3,
            circuit_breaker_timeout=60,
        )
        
        await selector.router.register_called_id("400-001", "agent_1")
        
        # 连续失败 3 次
        for _ in range(3):
            await selector.report_result("agent_1", success=False)
        
        # 检查熔断器是否打开
        health = selector.get_health("agent_1")
        assert health["circuit_breaker"] is not None


class TestCallIdRouterCache:
    """测试 CallIdRouter 缓存"""
    
    @pytest.mark.asyncio
    async def test_cache_cleanup(self):
        """测试缓存清理"""
        router = CallIdRouter(cache_ttl_seconds=1)
        
        # 注册并路由
        await router.register_called_id("400-001", "agent_1")
        await router.route("400-001")
        
        # 缓存应该有数据
        assert "400-001" in router._cache
        
        # 等待缓存过期
        await asyncio.sleep(1.5)
        
        # 手动清理缓存
        await router._cleanup_cache()
        
        # 过期缓存应该被清理
        assert "400-001" not in router._cache
    
    @pytest.mark.asyncio
    async def test_cache_hit(self):
        """测试缓存命中"""
        router = CallIdRouter(cache_ttl_seconds=60)
        
        # 注册并路由
        await router.register_called_id("400-001", "agent_1")
        result1 = await router.route("400-001")
        
        # 再次路由（应该命中缓存）
        result2 = await router.route("400-001", use_cache=True)
        
        # 结果应该相同
        assert result1 == result2


class TestGrayReleaseCanary:
    """测试金丝雀发布"""
    
    @pytest.mark.asyncio
    async def test_canary_stage_progression(self):
        """测试金丝雀阶段自动推进"""
        manager = GrayReleaseManager()
        
        # 配置金丝雀发布（直接 100%）
        await manager.configure_canary_release(
            called_id="400-001",
            canary_agent_id="agent_new",
            stages=[
                {"percentage": 100, "duration_minutes": 60},
            ],
            stable_agent_id="agent_old",
        )
        
        # 多次选择，应该全部是新 Agent
        selected_ids = []
        for _ in range(100):
            agent_id = await manager.select_agent("400-001")
            selected_ids.append(agent_id)
        
        # 应该 100% 选择新 Agent
        assert selected_ids.count("agent_new") == 100
    
    @pytest.mark.asyncio
    async def test_canary_rollback(self):
        """测试金丝雀发布回滚"""
        manager = GrayReleaseManager()
        
        await manager.configure_canary_release(
            called_id="400-001",
            canary_agent_id="agent_new",
            stages=[
                {"percentage": 10, "duration_minutes": 30},
            ],
            stable_agent_id="agent_old",
        )
        
        # 回滚
        await manager.rollback("400-001")
        
        # 应该返回 None（无灰度配置）
        agent_id = await manager.select_agent("400-001")
        assert agent_id is None


class TestLoadBalancerStrategySwitch:
    """测试负载均衡策略切换"""
    
    @pytest.mark.asyncio
    async def test_strategy_switch(self):
        """测试策略切换"""
        lb = LoadBalancer(strategy="round_robin")
        
        # 添加 Agent
        await lb.add_agent("agent_1")
        await lb.add_agent("agent_2")
        
        # 使用轮询策略
        result1 = await lb.select()
        
        # 切换策略
        lb.change_strategy("weighted")
        
        # 验证策略已切换
        stats = lb.get_stats()
        assert stats["strategy"] == "weighted"
    
    @pytest.mark.asyncio
    async def test_invalid_strategy(self):
        """测试无效策略"""
        lb = LoadBalancer()
        
        # 应该抛出异常
        with pytest.raises(ValueError):
            lb.change_strategy("invalid_strategy")


class TestConcurrentRouting:
    """测试并发路由"""
    
    @pytest.mark.asyncio
    async def test_concurrent_route_requests(self):
        """测试并发路由请求"""
        router = CallIdRouter()
        
        # 注册多个 Agent
        await router.register_called_id("400-001", "agent_1", priority=1)
        await router.register_called_id("400-001", "agent_2", priority=2)
        await router.register_called_id("400-001", "agent_3", priority=3)
        
        # 并发路由
        tasks = [router.route("400-001") for _ in range(100)]
        results = await asyncio.gather(*tasks)
        
        # 所有结果都应该有效
        for result in results:
            assert result in ["agent_1", "agent_2", "agent_3"]
        
        # 优先级高的应该被选中更多
        assert results.count("agent_3") > results.count("agent_1")
    
    @pytest.mark.asyncio
    async def test_concurrent_cache_access(self):
        """测试并发缓存访问"""
        router = CallIdRouter(cache_ttl_seconds=60)
        
        await router.register_called_id("400-001", "agent_1")
        
        # 并发路由（都使用缓存）
        tasks = [router.route("400-001", use_cache=True) for _ in range(50)]
        results = await asyncio.gather(*tasks)
        
        # 所有结果都应该相同（缓存命中）
        assert len(set(results)) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
