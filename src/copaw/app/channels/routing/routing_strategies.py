"""
路由策略

定义多种路由策略：轮询、权重、优先级、最少连接
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time


@dataclass
class AgentInfo:
    """Agent 信息"""
    agent_id: str
    priority: int = 0
    weight: int = 100
    is_active: bool = True
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class RoutingStrategy(ABC):
    """
    路由策略基类
    
    子类实现具体的路由算法
    """
    
    @abstractmethod
    def select_agent(
        self,
        agents: List[AgentInfo],
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[AgentInfo]:
        """
        选择 Agent
        
        Args:
            agents: 候选 Agent 列表
            context: 路由上下文（可选）
        
        Returns:
            选中的 AgentInfo，如果没有可用 Agent 返回 None
        """
        pass
    
    @abstractmethod
    def report_result(
        self,
        agent_id: str,
        success: bool,
        latency_ms: Optional[float] = None,
    ):
        """
        报告路由结果（用于自适应调整）
        
        Args:
            agent_id: Agent ID
            success: 是否成功
            latency_ms: 延迟（毫秒）
        """
        pass


class RoundRobinStrategy(RoutingStrategy):
    """
    轮询策略
    
    按顺序轮流选择 Agent，实现简单负载均衡
    
    注意：本策略是无状态的，索引通过 context 传递，确保线程安全
    """
    
    def select_agent(
        self,
        agents: List[AgentInfo],
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[AgentInfo]:
        """轮询选择 Agent（线程安全）"""
        if not agents:
            return None
        
        # 过滤活跃 Agent
        active_agents = [a for a in agents if a.is_active]
        if not active_agents:
            return None
        
        # 从 context 读取索引（线程安全）
        if context is None:
            context = {}
        
        index = context.get("round_robin_index", 0)
        index = index % len(active_agents)
        selected = active_agents[index]
        
        # 更新索引
        context["round_robin_index"] = index + 1
        
        return selected
    
    def report_result(
        self,
        agent_id: str,
        success: bool,
        latency_ms: Optional[float] = None,
    ):
        """轮询策略不需要报告结果"""
        pass


class WeightedStrategy(RoutingStrategy):
    """
    权重策略
    
    根据权重比例选择 Agent，权重越高被选中的概率越大
    """
    
    def __init__(self):
        self._index = 0
    
    def select_agent(
        self,
        agents: List[AgentInfo],
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[AgentInfo]:
        """加权随机选择 Agent"""
        if not agents:
            return None
        
        # 过滤活跃 Agent
        active_agents = [a for a in agents if a.is_active]
        if not active_agents:
            return None
        
        # 计算总权重
        total_weight = sum(a.weight for a in active_agents)
        if total_weight == 0:
            # 所有权重为 0，随机选择
            import random
            return random.choice(active_agents)
        
        # 按权重随机选择
        import random
        rand = random.uniform(0, total_weight)
        current = 0
        
        for agent in active_agents:
            current += agent.weight
            if rand <= current:
                return agent
        
        # 应该不会到这里
        return active_agents[-1]
    
    def report_result(
        self,
        agent_id: str,
        success: bool,
        latency_ms: Optional[float] = None,
    ):
        """权重策略不需要报告结果"""
        pass


class PriorityStrategy(RoutingStrategy):
    """
    优先级策略
    
    优先选择优先级高的 Agent，优先级相同则轮询
    """
    
    def select_agent(
        self,
        agents: List[AgentInfo],
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[AgentInfo]:
        """按优先级选择 Agent"""
        if not agents:
            return None
        
        # 过滤活跃 Agent
        active_agents = [a for a in agents if a.is_active]
        if not active_agents:
            return None
        
        # 按优先级排序（降序）
        sorted_agents = sorted(active_agents, key=lambda a: a.priority, reverse=True)
        
        # 获取最高优先级
        max_priority = sorted_agents[0].priority
        
        # 在最高优先级中轮询
        same_priority_agents = [a for a in sorted_agents if a.priority == max_priority]
        
        # 简单轮询
        index = hash(str(time.time())) % len(same_priority_agents)
        return same_priority_agents[index]
    
    def report_result(
        self,
        agent_id: str,
        success: bool,
        latency_ms: Optional[float] = None,
    ):
        """优先级策略不需要报告结果"""
        pass


class LeastConnectionsStrategy(RoutingStrategy):
    """
    最少连接策略
    
    选择当前连接数最少的 Agent，适合长连接场景
    """
    
    def __init__(self):
        self._connection_counts: Dict[str, int] = {}
        self._response_times: Dict[str, List[float]] = {}
    
    def select_agent(
        self,
        agents: List[AgentInfo],
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[AgentInfo]:
        """选择连接数最少的 Agent"""
        if not agents:
            return None
        
        # 过滤活跃 Agent
        active_agents = [a for a in agents if a.is_active]
        if not active_agents:
            return None
        
        # 选择连接数最少的 Agent
        def get_connection_count(agent: AgentInfo) -> int:
            return self._connection_counts.get(agent.agent_id, 0)
        
        selected = min(active_agents, key=get_connection_count)
        
        # 增加连接数
        self._connection_counts[selected.agent_id] = get_connection_count(selected) + 1
        
        return selected
    
    def report_result(
        self,
        agent_id: str,
        success: bool,
        latency_ms: Optional[float] = None,
    ):
        """报告结果，减少连接数"""
        if agent_id in self._connection_counts:
            self._connection_counts[agent_id] = max(0, self._connection_counts[agent_id] - 1)
        
        # 记录响应时间（用于后续优化）
        if latency_ms is not None:
            if agent_id not in self._response_times:
                self._response_times[agent_id] = []
            self._response_times[agent_id].append(latency_ms)
            # 保留最近 100 次
            if len(self._response_times[agent_id]) > 100:
                self._response_times[agent_id] = self._response_times[agent_id][-100:]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "connection_counts": self._connection_counts.copy(),
            "avg_response_times": {
                agent_id: sum(times) / len(times) if times else 0
                for agent_id, times in self._response_times.items()
            },
        }


class AdaptiveStrategy(RoutingStrategy):
    """
    自适应策略
    
    根据历史表现动态调整权重，选择最优 Agent
    """
    
    def __init__(self, base_weights: Optional[Dict[str, int]] = None):
        self._base_weights = base_weights or {}
        self._dynamic_weights: Dict[str, float] = {}
        self._success_rates: Dict[str, float] = {}
        self._avg_latencies: Dict[str, float] = {}
        self._request_counts: Dict[str, int] = {}
        self._success_counts: Dict[str, int] = {}
    
    def select_agent(
        self,
        agents: List[AgentInfo],
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[AgentInfo]:
        """根据动态权重选择 Agent"""
        if not agents:
            return None
        
        # 过滤活跃 Agent
        active_agents = [a for a in agents if a.is_active]
        if not active_agents:
            return None
        
        # 计算动态权重
        weighted_agents = []
        for agent in active_agents:
            base_weight = self._base_weights.get(agent.agent_id, agent.weight)
            dynamic_weight = self._dynamic_weights.get(agent.agent_id, 1.0)
            final_weight = int(base_weight * dynamic_weight)
            
            weighted_agents.append(AgentInfo(
                agent_id=agent.agent_id,
                priority=agent.priority,
                weight=final_weight,
                is_active=agent.is_active,
                metadata=agent.metadata,
            ))
        
        # 使用加权策略
        weighted_strategy = WeightedStrategy()
        return weighted_strategy.select_agent(weighted_agents)
    
    def report_result(
        self,
        agent_id: str,
        success: bool,
        latency_ms: Optional[float] = None,
    ):
        """报告结果，更新动态权重"""
        # 更新计数
        if agent_id not in self._request_counts:
            self._request_counts[agent_id] = 0
            self._success_counts[agent_id] = 0
            self._dynamic_weights[agent_id] = 1.0
        
        self._request_counts[agent_id] += 1
        if success:
            self._success_counts[agent_id] += 1
        
        # 计算成功率
        self._success_rates[agent_id] = (
            self._success_counts[agent_id] / self._request_counts[agent_id]
        )
        
        # 更新平均延迟
        if latency_ms is not None:
            if agent_id not in self._avg_latencies:
                self._avg_latencies[agent_id] = latency_ms
            else:
                # 移动平均
                self._avg_latencies[agent_id] = (
                    0.9 * self._avg_latencies[agent_id] + 0.1 * latency_ms
                )
        
        # 计算动态权重（基于成功率和延迟）
        success_rate = self._success_rates[agent_id]
        avg_latency = self._avg_latencies.get(agent_id, 100)
        
        # 成功率权重（0-1）
        success_weight = success_rate
        
        # 延迟权重（归一化，假设 1000ms 为最差）
        latency_weight = max(0, 1 - (avg_latency / 1000))
        
        # 综合权重
        self._dynamic_weights[agent_id] = 0.7 * success_weight + 0.3 * latency_weight
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "success_rates": self._success_rates.copy(),
            "avg_latencies": self._avg_latencies.copy(),
            "dynamic_weights": self._dynamic_weights.copy(),
            "request_counts": self._request_counts.copy(),
        }
