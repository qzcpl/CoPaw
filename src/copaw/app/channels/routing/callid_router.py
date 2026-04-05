"""
CalledId 路由器

实现 CalledId 到 Agent 的路由机制，支持携号转网
"""

import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from .routing_strategies import (
    RoutingStrategy,
    PriorityStrategy,
    AgentInfo,
)


class CallIdRouter:
    """
    CalledId 路由器
    
    实现 CalledId 到 Agent 的路由机制
    
    功能：
    1. CalledId 注册/注销
    2. Agent 绑定/解绑
    3. 路由查询（支持策略）
    4. 负载均衡
    5. 故障转移
    """
    
    def __init__(
        self,
        default_strategy: Optional[RoutingStrategy] = None,
        cache_ttl_seconds: int = 60,
    ):
        """
        Args:
            default_strategy: 默认路由策略
            cache_ttl_seconds: 缓存 TTL
        """
        self.default_strategy = default_strategy or PriorityStrategy()
        self.cache_ttl = timedelta(seconds=cache_ttl_seconds)
        
        # CalledId 路由表：called_id -> [AgentInfo]
        self._routes: Dict[str, List[AgentInfo]] = {}
        
        # 缓存
        self._cache: Dict[str, tuple] = {}  # called_id -> (agent_id, expires_at)
        
        # 锁
        self._locks: Dict[str, asyncio.Lock] = {}
    
    def _get_lock(self, called_id: str) -> asyncio.Lock:
        """获取异步锁"""
        if called_id not in self._locks:
            self._locks[called_id] = asyncio.Lock()
        return self._locks[called_id]
    
    async def register_called_id(
        self,
        called_id: str,
        agent_id: str,
        priority: int = 0,
        weight: int = 100,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        注册 CalledId
        
        Args:
            called_id: 被叫 ID
            agent_id: Agent ID
            priority: 优先级
            weight: 权重
            metadata: 扩展元数据
        """
        async with self._get_lock(called_id):
            if called_id not in self._routes:
                self._routes[called_id] = []
            
            # 检查是否已存在
            for i, agent in enumerate(self._routes[called_id]):
                if agent.agent_id == agent_id:
                    # 更新现有记录
                    self._routes[called_id][i] = AgentInfo(
                        agent_id=agent_id,
                        priority=priority,
                        weight=weight,
                        is_active=True,
                        metadata=metadata or {},
                    )
                    return
            
            # 添加新记录
            self._routes[called_id].append(AgentInfo(
                agent_id=agent_id,
                priority=priority,
                weight=weight,
                is_active=True,
                metadata=metadata or {},
            ))
    
    async def unregister_called_id(self, called_id: str, agent_id: str):
        """
        注销 CalledId
        
        Args:
            called_id: 被叫 ID
            agent_id: Agent ID
        """
        async with self._get_lock(called_id):
            if called_id not in self._routes:
                return
            
            # 移除记录
            self._routes[called_id] = [
                a for a in self._routes[called_id]
                if a.agent_id != agent_id
            ]
            
            # 如果没有 Agent 了，删除路由
            if not self._routes[called_id]:
                del self._routes[called_id]
            
            # 清除缓存
            if called_id in self._cache:
                del self._cache[called_id]
    
    async def set_agent_active(
        self,
        called_id: str,
        agent_id: str,
        is_active: bool,
    ):
        """
        设置 Agent 激活状态
        
        Args:
            called_id: 被叫 ID
            agent_id: Agent ID
            is_active: 是否激活
        """
        async with self._get_lock(called_id):
            if called_id not in self._routes:
                return
            
            for i, agent in enumerate(self._routes[called_id]):
                if agent.agent_id == agent_id:
                    self._routes[called_id][i] = AgentInfo(
                        agent_id=agent_id,
                        priority=agent.priority,
                        weight=agent.weight,
                        is_active=is_active,
                        metadata=agent.metadata,
                    )
                    break
    
    async def route(
        self,
        called_id: str,
        strategy: Optional[RoutingStrategy] = None,
        use_cache: bool = True,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        路由查询
        
        Args:
            called_id: 被叫 ID
            strategy: 路由策略（可选，默认使用默认策略）
            use_cache: 是否使用缓存
            context: 路由上下文
        
        Returns:
            Agent ID，如果没有可用 Agent 返回 None
        """
        # 清理过期缓存（惰性清理）
        await self._cleanup_cache()
        
        # 尝试缓存
        if use_cache and called_id in self._cache:
            agent_id, expires_at = self._cache[called_id]
            if expires_at > datetime.now():
                return agent_id
            else:
                del self._cache[called_id]
        
        # 获取锁
        async with self._get_lock(called_id):
            # 双重检查缓存
            if use_cache and called_id in self._cache:
                agent_id, expires_at = self._cache[called_id]
                if expires_at > datetime.now():
                    return agent_id
            
            # 获取路由
            if called_id not in self._routes:
                return None
            
            agents = self._routes[called_id]
            if not agents:
                return None
            
            # 选择策略
            strategy = strategy or self.default_strategy
            
            # 选择 Agent
            selected = strategy.select_agent(agents, context)
            
            if not selected:
                return None
            
            # 缓存结果
            self._cache[called_id] = (
                selected.agent_id,
                datetime.now() + self.cache_ttl,
            )
            
            return selected.agent_id
    
    async def get_agents(self, called_id: str) -> List[Dict[str, Any]]:
        """
        获取 CalledId 的所有 Agent
        
        Args:
            called_id: 被叫 ID
        
        Returns:
            Agent 信息列表
        """
        if called_id not in self._routes:
            return []
        
        return [
            {
                "agent_id": a.agent_id,
                "priority": a.priority,
                "weight": a.weight,
                "is_active": a.is_active,
                "metadata": a.metadata,
            }
            for a in self._routes[called_id]
        ]
    
    async def get_stats(self, called_id: str) -> Dict[str, Any]:
        """
        获取路由统计信息
        
        Args:
            called_id: 被叫 ID
        
        Returns:
            统计信息
        """
        if called_id not in self._routes:
            return {"total_agents": 0, "active_agents": 0}
        
        agents = self._routes[called_id]
        active_agents = [a for a in agents if a.is_active]
        
        return {
            "total_agents": len(agents),
            "active_agents": len(active_agents),
            "agents": [
                {
                    "agent_id": a.agent_id,
                    "priority": a.priority,
                    "weight": a.weight,
                    "is_active": a.is_active,
                }
                for a in agents
            ],
        }
    
    async def _cleanup_cache(self):
        """
        清理过期缓存（惰性清理）
        
        定期调用此方法清理过期缓存项，避免内存泄漏
        """
        now = datetime.now()
        expired = [
            k for k, (_, expires_at) in self._cache.items()
            if expires_at < now
        ]
        for k in expired:
            del self._cache[k]
    
    def clear_cache(self, called_id: Optional[str] = None):
        """
        清除缓存
        
        Args:
            called_id: 被叫 ID（可选，为 None 时清除所有）
        """
        if called_id:
            if called_id in self._cache:
                del self._cache[called_id]
        else:
            self._cache.clear()
    
    async def load_from_database(self):
        """
        从数据库加载路由配置
        
        TODO: 实现数据库加载
        """
        # 示例代码：
        # from copaw.app.database import get_session
        # from copaw.app.database.models import IdentifierRegistry
        #
        # with get_session() as session:
        #     records = session.query(IdentifierRegistry).filter(
        #         IdentifierRegistry.is_active == True
        #     ).all()
        #
        #     for record in records:
        #         await self.register_called_id(
        #             called_id=record.called_id,
        #             agent_id=record.agent_id,
        #             priority=record.priority,
        #             weight=record.weight,
        #             metadata=record.metadata,
        #         )
        pass
    
    async def save_to_database(self):
        """
        保存路由配置到数据库
        
        TODO: 实现数据库保存
        """
        pass
