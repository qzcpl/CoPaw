"""
负载均衡器

实现多种负载均衡算法
"""

import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime

from .routing_strategies import (
    RoutingStrategy,
    RoundRobinStrategy,
    WeightedStrategy,
    LeastConnectionsStrategy,
    AdaptiveStrategy,
    AgentInfo,
)


class LoadBalancer:
    """
    负载均衡器
    
    封装多种负载均衡策略
    
    支持的策略：
    1. 轮询（Round Robin）
    2. 加权轮询（Weighted）
    3. 最少连接（Least Connections）
    4. 自适应（Adaptive）
    """
    
    def __init__(self, strategy: str = "round_robin"):
        """
        Args:
            strategy: 负载均衡策略
                - "round_robin": 轮询
                - "weighted": 加权轮询
                - "least_connections": 最少连接
                - "adaptive": 自适应
        """
        self.strategy_name = strategy
        self._strategy = self._create_strategy(strategy)
        self._agents: Dict[str, AgentInfo] = {}
        self._lock = asyncio.Lock()
    
    def _create_strategy(self, strategy: str) -> RoutingStrategy:
        """创建策略实例"""
        strategies = {
            "round_robin": RoundRobinStrategy(),
            "weighted": WeightedStrategy(),
            "least_connections": LeastConnectionsStrategy(),
            "adaptive": AdaptiveStrategy(),
        }
        
        if strategy not in strategies:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        return strategies[strategy]
    
    async def add_agent(
        self,
        agent_id: str,
        priority: int = 0,
        weight: int = 100,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        添加 Agent
        
        Args:
            agent_id: Agent ID
            priority: 优先级
            weight: 权重
            metadata: 元数据
        """
        async with self._lock:
            self._agents[agent_id] = AgentInfo(
                agent_id=agent_id,
                priority=priority,
                weight=weight,
                is_active=True,
                metadata=metadata or {},
            )
    
    async def remove_agent(self, agent_id: str):
        """
        移除 Agent
        
        Args:
            agent_id: Agent ID
        """
        async with self._lock:
            if agent_id in self._agents:
                del self._agents[agent_id]
    
    async def set_agent_active(self, agent_id: str, is_active: bool):
        """
        设置 Agent 激活状态
        
        Args:
            agent_id: Agent ID
            is_active: 是否激活
        """
        async with self._lock:
            if agent_id in self._agents:
                self._agents[agent_id].is_active = is_active
    
    async def select(self) -> Optional[str]:
        """
        选择 Agent
        
        Returns:
            Agent ID
        """
        async with self._lock:
            agents = list(self._agents.values())
        
        if not agents:
            return None
        
        selected = self._strategy.select_agent(agents)
        return selected.agent_id if selected else None
    
    async def report_result(
        self,
        agent_id: str,
        success: bool,
        latency_ms: Optional[float] = None,
    ):
        """
        报告调用结果
        
        Args:
            agent_id: Agent ID
            success: 是否成功
            latency_ms: 延迟
        """
        self._strategy.report_result(agent_id, success, latency_ms)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "strategy": self.strategy_name,
            "total_agents": len(self._agents),
            "active_agents": sum(1 for a in self._agents.values() if a.is_active),
            "agents": [
                {
                    "agent_id": a.agent_id,
                    "priority": a.priority,
                    "weight": a.weight,
                    "is_active": a.is_active,
                }
                for a in self._agents.values()
            ],
        }
    
    def change_strategy(self, strategy: str):
        """
        切换负载均衡策略
        
        Args:
            strategy: 新策略名称
        """
        self._strategy = self._create_strategy(strategy)
        self.strategy_name = strategy
