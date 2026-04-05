"""
Agent 选择器

封装 Agent 选择逻辑，支持健康检查、故障转移
"""

import asyncio
from typing import Optional, Dict, Any, List, Callable, Awaitable
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from .callid_router import CallIdRouter
from .routing_strategies import RoutingStrategy


@dataclass
class AgentHealth:
    """Agent 健康状态"""
    agent_id: str
    is_healthy: bool = True
    last_check: datetime = field(default_factory=datetime.now)
    consecutive_failures: int = 0
    last_failure: Optional[datetime] = None
    response_time_ms: float = 0.0
    error_rate: float = 0.0


class AgentSelector:
    """
    Agent 选择器
    
    封装 Agent 选择逻辑，提供高级功能
    
    功能：
    1. 健康检查
    2. 故障转移
    3. 熔断器
    4. 性能监控
    """
    
    def __init__(
        self,
        router: Optional[CallIdRouter] = None,
        health_check_interval: int = 30,  # 秒
        failure_threshold: int = 5,  # 连续失败次数阈值
        recovery_timeout: int = 60,  # 恢复超时（秒）
        circuit_breaker_timeout: int = 30,  # 熔断超时（秒）
    ):
        """
        Args:
            router: CalledId 路由器
            health_check_interval: 健康检查间隔
            failure_threshold: 失败阈值
            recovery_timeout: 恢复超时
            circuit_breaker_timeout: 熔断超时
        """
        self.router = router or CallIdRouter()
        self.health_check_interval = health_check_interval
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.circuit_breaker_timeout = circuit_breaker_timeout
        
        # 健康状态
        self._health_map: Dict[str, AgentHealth] = {}
        
        # 熔断器状态
        self._circuit_breakers: Dict[str, datetime] = {}  # agent_id -> opens_at
        
        # 性能指标
        self._metrics: Dict[str, Dict[str, Any]] = {}
        
        # 后台任务
        self._health_check_task: Optional[asyncio.Task] = None
    
    async def start_health_check(self):
        """启动健康检查后台任务"""
        if self._health_check_task is None:
            self._health_check_task = asyncio.create_task(
                self._health_check_loop()
            )
    
    async def stop_health_check(self):
        """停止健康检查后台任务"""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self._health_check_task = None
    
    async def _health_check_loop(self):
        """健康检查循环"""
        try:
            while True:
                await asyncio.sleep(self.health_check_interval)
                await self._check_all_agents()
        except asyncio.CancelledError:
            pass
    
    async def _check_all_agents(self):
        """检查所有 Agent 健康状态"""
        # TODO: 实现健康检查逻辑
        # 可以通过 ping 或简单请求检查
        pass
    
    async def select_agent(
        self,
        called_id: str,
        strategy: Optional[RoutingStrategy] = None,
        exclude_unhealthy: bool = True,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        选择 Agent
        
        Args:
            called_id: 被叫 ID
            strategy: 路由策略
            exclude_unhealthy: 是否排除不健康 Agent
            context: 路由上下文
        
        Returns:
            Agent ID
        """
        # 获取所有 Agent
        agents = await self.router.get_agents(called_id)
        if not agents:
            return None
        
        # 过滤不健康 Agent
        if exclude_unhealthy:
            healthy_agents = []
            for agent in agents:
                agent_id = agent["agent_id"]
                
                # 检查熔断器
                if agent_id in self._circuit_breakers:
                    if self._circuit_breakers[agent_id] > datetime.now():
                        # 熔断中，跳过
                        continue
                    else:
                        # 熔断超时，尝试恢复
                        del self._circuit_breakers[agent_id]
                
                # 检查健康状态
                health = self._health_map.get(agent_id)
                if health and not health.is_healthy:
                    # 检查是否应该恢复
                    if health.last_failure:
                        time_since_failure = (
                            datetime.now() - health.last_failure
                        ).total_seconds()
                        if time_since_failure < self.recovery_timeout:
                            continue
                
                healthy_agents.append(agent)
            
            agents = healthy_agents
        
        if not agents:
            return None
        
        # 转换为 AgentInfo
        from .routing_strategies import AgentInfo
        agent_infos = [
            AgentInfo(
                agent_id=a["agent_id"],
                priority=a["priority"],
                weight=a["weight"],
                is_active=a["is_active"],
                metadata=a.get("metadata", {}),
            )
            for a in agents
        ]
        
        # 使用路由器选择
        agent_id = await self.router.route(
            called_id=called_id,
            strategy=strategy,
            use_cache=False,  # 已经过滤，不使用缓存
            context=context,
        )
        
        return agent_id
    
    async def report_result(
        self,
        agent_id: str,
        success: bool,
        latency_ms: Optional[float] = None,
        error: Optional[str] = None,
    ):
        """
        报告调用结果
        
        Args:
            agent_id: Agent ID
            success: 是否成功
            latency_ms: 延迟
            error: 错误信息
        """
        # 初始化健康状态
        if agent_id not in self._health_map:
            self._health_map[agent_id] = AgentHealth(agent_id=agent_id)
        
        health = self._health_map[agent_id]
        
        if success:
            # 成功：重置失败计数
            health.consecutive_failures = 0
            health.is_healthy = True
            health.last_check = datetime.now()
            
            if latency_ms is not None:
                health.response_time_ms = (
                    0.9 * health.response_time_ms + 0.1 * latency_ms
                )
        else:
            # 失败：增加失败计数
            health.consecutive_failures += 1
            health.last_failure = datetime.now()
            health.last_check = datetime.now()
            
            # 检查是否触发熔断
            if health.consecutive_failures >= self.failure_threshold:
                self._circuit_breakers[agent_id] = (
                    datetime.now() + timedelta(seconds=self.circuit_breaker_timeout)
                )
                print(f"⚡ Circuit breaker opened for {agent_id}")
        
        # 更新指标
        self._update_metrics(agent_id, success, latency_ms, error)
    
    def _update_metrics(
        self,
        agent_id: str,
        success: bool,
        latency_ms: Optional[float],
        error: Optional[str],
    ):
        """更新性能指标"""
        if agent_id not in self._metrics:
            self._metrics[agent_id] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_latency_ms": 0.0,
                "last_error": None,
            }
        
        metrics = self._metrics[agent_id]
        metrics["total_requests"] += 1
        
        if success:
            metrics["successful_requests"] += 1
        else:
            metrics["failed_requests"] += 1
            metrics["last_error"] = error
        
        if latency_ms is not None:
            metrics["total_latency_ms"] += latency_ms
    
    def get_health(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        获取 Agent 健康状态
        
        Args:
            agent_id: Agent ID
        
        Returns:
            健康状态字典
        """
        if agent_id not in self._health_map:
            return None
        
        health = self._health_map[agent_id]
        
        return {
            "agent_id": health.agent_id,
            "is_healthy": health.is_healthy,
            "last_check": health.last_check.isoformat(),
            "consecutive_failures": health.consecutive_failures,
            "last_failure": health.last_failure.isoformat() if health.last_failure else None,
            "response_time_ms": health.response_time_ms,
            "circuit_breaker": (
                self._circuit_breakers.get(agent_id, datetime.min).isoformat()
                if agent_id in self._circuit_breakers
                else None
            ),
        }
    
    def get_metrics(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        获取 Agent 性能指标
        
        Args:
            agent_id: Agent ID
        
        Returns:
            性能指标字典
        """
        if agent_id not in self._metrics:
            return None
        
        metrics = self._metrics[agent_id]
        total = metrics["total_requests"]
        
        return {
            "agent_id": agent_id,
            "total_requests": total,
            "successful_requests": metrics["successful_requests"],
            "failed_requests": metrics["failed_requests"],
            "success_rate": metrics["successful_requests"] / total if total > 0 else 0,
            "avg_latency_ms": (
                metrics["total_latency_ms"] / total if total > 0 else 0
            ),
            "last_error": metrics["last_error"],
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有 Agent 统计信息"""
        return {
            "health": {
                agent_id: self.get_health(agent_id)
                for agent_id in self._health_map
            },
            "metrics": {
                agent_id: self.get_metrics(agent_id)
                for agent_id in self._metrics
            },
            "circuit_breakers": {
                agent_id: expires_at.isoformat()
                for agent_id, expires_at in self._circuit_breakers.items()
            },
        }
