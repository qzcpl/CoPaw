"""
灰度发布管理器

实现灰度发布、金丝雀发布、A/B 测试
"""

import asyncio
from typing import Optional, Dict, Any, List, Set
from datetime import datetime, timedelta
import random
import hashlib


class GrayReleaseManager:
    """
    灰度发布管理器
    
    支持多种灰度策略：
    1. 百分比灰度（按流量比例）
    2. 用户灰度（按用户 ID）
    3. 地域灰度（按地域）
    4. 金丝雀发布（逐步扩大）
    """
    
    def __init__(self):
        # 灰度配置：called_id -> GrayReleaseConfig
        self._configs: Dict[str, Dict[str, Any]] = {}
        
        # 金丝雀发布状态
        self._canary_releases: Dict[str, Dict[str, Any]] = {}
        
        self._lock = asyncio.Lock()
    
    async def configure_percentage_release(
        self,
        called_id: str,
        canary_agent_id: str,
        percentage: float,
        stable_agent_id: Optional[str] = None,
    ):
        """
        配置百分比灰度
        
        Args:
            called_id: 被叫 ID
            canary_agent_id: 金丝雀 Agent ID（新版本）
            percentage: 灰度百分比（0-100）
            stable_agent_id: 稳定版 Agent ID（可选）
        """
        async with self._lock:
            self._configs[called_id] = {
                "type": "percentage",
                "canary_agent_id": canary_agent_id,
                "stable_agent_id": stable_agent_id,
                "percentage": percentage,
                "created_at": datetime.now(),
            }
    
    async def configure_user_release(
        self,
        called_id: str,
        canary_agent_id: str,
        user_ids: List[str],
        stable_agent_id: Optional[str] = None,
    ):
        """
        配置用户灰度
        
        Args:
            called_id: 被叫 ID
            canary_agent_id: 金丝雀 Agent ID
            user_ids: 灰度用户 ID 列表
            stable_agent_id: 稳定版 Agent ID
        """
        async with self._lock:
            self._configs[called_id] = {
                "type": "user",
                "canary_agent_id": canary_agent_id,
                "stable_agent_id": stable_agent_id,
                "user_ids": set(user_ids),
                "created_at": datetime.now(),
            }
    
    async def configure_canary_release(
        self,
        called_id: str,
        canary_agent_id: str,
        stages: List[Dict[str, Any]],
        stable_agent_id: Optional[str] = None,
    ):
        """
        配置金丝雀发布
        
        Args:
            called_id: 被叫 ID
            canary_agent_id: 金丝雀 Agent ID
            stages: 发布阶段配置
                [
                    {"percentage": 10, "duration_minutes": 30},
                    {"percentage": 50, "duration_minutes": 60},
                    {"percentage": 100, "duration_minutes": 0},
                ]
            stable_agent_id: 稳定版 Agent ID
        """
        async with self._lock:
            self._canary_releases[called_id] = {
                "canary_agent_id": canary_agent_id,
                "stable_agent_id": stable_agent_id,
                "stages": stages,
                "current_stage": 0,
                "started_at": datetime.now(),
                "current_percentage": stages[0]["percentage"] if stages else 0,
            }
    
    async def select_agent(
        self,
        called_id: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        根据灰度配置选择 Agent
        
        Args:
            called_id: 被叫 ID
            user_id: 用户 ID（用于用户灰度）
            context: 上下文
        
        Returns:
            Agent ID
        """
        async with self._lock:
            # 检查是否有灰度配置
            if called_id not in self._configs and called_id not in self._canary_releases:
                return None
            
            # 优先使用金丝雀发布配置
            if called_id in self._canary_releases:
                return await self._select_canary_agent(called_id, user_id, context)
            
            # 使用灰度配置
            if called_id in self._configs:
                return await self._select_gray_agent(called_id, user_id, context)
        
        return None
    
    async def _select_gray_agent(
        self,
        called_id: str,
        user_id: Optional[str],
        context: Optional[Dict[str, Any]],
    ) -> str:
        """选择灰度 Agent"""
        config = self._configs[called_id]
        config_type = config["type"]
        
        if config_type == "percentage":
            # 百分比灰度
            percentage = config["percentage"]
            if random.random() * 100 < percentage:
                return config["canary_agent_id"]
            else:
                return config.get("stable_agent_id") or config["canary_agent_id"]
        
        elif config_type == "user":
            # 用户灰度
            user_ids = config["user_ids"]
            if user_id and user_id in user_ids:
                return config["canary_agent_id"]
            else:
                return config.get("stable_agent_id") or config["canary_agent_id"]
        
        # 默认返回金丝雀 Agent
        return config["canary_agent_id"]
    
    async def _select_canary_agent(
        self,
        called_id: str,
        user_id: Optional[str],
        context: Optional[Dict[str, Any]],
    ) -> str:
        """选择金丝雀 Agent"""
        release = self._canary_releases[called_id]
        
        # 检查是否需要切换到下一阶段
        await self._check_canary_stage(called_id)
        
        # 根据当前百分比决定
        current_percentage = release["current_percentage"]
        
        if random.random() * 100 < current_percentage:
            return release["canary_agent_id"]
        else:
            return release.get("stable_agent_id") or release["canary_agent_id"]
    
    async def _check_canary_stage(self, called_id: str):
        """检查是否需要切换金丝雀阶段"""
        if called_id not in self._canary_releases:
            return
        
        release = self._canary_releases[called_id]
        stages = release["stages"]
        current_stage = release["current_stage"]
        started_at = release["started_at"]
        
        # 检查是否已完成所有阶段
        if current_stage >= len(stages):
            return
        
        # 检查当前阶段是否应该结束
        stage = stages[current_stage]
        duration_minutes = stage.get("duration_minutes", 0)
        
        if duration_minutes > 0:
            elapsed = (datetime.now() - started_at).total_seconds() / 60
            if elapsed >= duration_minutes:
                # 切换到下一阶段
                release["current_stage"] += 1
                if release["current_stage"] < len(stages):
                    release["current_percentage"] = stages[release["current_stage"]]["percentage"]
                else:
                    release["current_percentage"] = 100
    
    async def update_percentage(
        self,
        called_id: str,
        percentage: float,
    ):
        """
        更新灰度百分比
        
        Args:
            called_id: 被叫 ID
            percentage: 新百分比
        """
        async with self._lock:
            if called_id in self._configs:
                self._configs[called_id]["percentage"] = percentage
    
    async def rollback(self, called_id: str):
        """
        回滚灰度发布
        
        Args:
            called_id: 被叫 ID
        """
        async with self._lock:
            if called_id in self._configs:
                del self._configs[called_id]
            if called_id in self._canary_releases:
                del self._canary_releases[called_id]
    
    def get_config(self, called_id: str) -> Optional[Dict[str, Any]]:
        """获取灰度配置"""
        config = self._configs.get(called_id)
        if config:
            return config.copy()
        
        release = self._canary_releases.get(called_id)
        if release:
            return {
                "type": "canary",
                **release,
            }
        
        return None
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """获取所有灰度配置"""
        return {
            **self._configs,
            **{
                k: {"type": "canary", **v}
                for k, v in self._canary_releases.items()
            },
        }
