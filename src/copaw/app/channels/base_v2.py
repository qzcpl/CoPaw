"""
BaseChannel v2 - 支持适配器模式和六层标识体系

基于原有 BaseChannel 升级，增加：
1. 适配器支持（DingTalk/Feishu 等）
2. 六层标识符支持
3. SessionContext 注入
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC
from typing import (
    Optional,
    Dict,
    Any,
    List,
    Union,
    AsyncIterator,
    Callable,
    TYPE_CHECKING,
)

# 导入阶段 1-3 的模块
import sys
from pathlib import Path

patch_src = Path(__file__).parent.parent.parent
sys.path.insert(0, str(patch_src))

from copaw.identifier.schemas import (
    Identifiers,
    ChannelId,
    CallerLogicalId,
    CallerPhysicalId,
    CalledId,
    SessionId,
    MessageId,
    CallerType,
)
from copaw.app.channels.schema import BusMessage, SessionContext

# 导入适配器
try:
    from .adapters.base import BaseAdapter
    from .adapters.dingtalk import DingTalkAdapter
    from .adapters.feishu import FeishuAdapter
except ImportError:
    BaseAdapter = None
    DingTalkAdapter = None
    FeishuAdapter = None

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from agentscope_runtime.engine.schemas.agent_schemas import (
        AgentRequest,
        AgentResponse,
        Event,
    )


class BaseChannelV2(ABC):
    """
    BaseChannel v2 - 支持适配器模式
    
    主要升级：
    1. 支持六层标识符
    2. 支持 SessionContext 注入
    3. 支持适配器模式
    4. 保持向后兼容
    """
    
    # 频道标识
    channel: str = "unknown"
    
    # 是否使用管理器队列
    uses_manager_queue: bool = True
    
    # 适配器（子类可设置）
    adapter_class: Optional[type] = None
    
    def __init__(
        self,
        process: Callable[[Any], AsyncIterator["Event"]],
        config: Optional[Dict[str, Any]] = None,
        adapter_config: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """
        Args:
            process: 消息处理函数
            config: 频道配置
            adapter_config: 适配器配置
            **kwargs: 其他参数（兼容旧版）
        """
        self._process = process
        self.config = config or {}
        
        # 初始化适配器
        self.adapter: Optional[BaseAdapter] = None
        if self.adapter_class and BaseAdapter:
            self.adapter = self.adapter_class(adapter_config)
        
        # 其他配置
        self._show_tool_details = kwargs.get("show_tool_details", True)
        self._filter_tool_messages = kwargs.get("filter_tool_messages", False)
        self._filter_thinking = kwargs.get("filter_thinking", False)
    
    async def receive_message(
        self,
        raw_message: Dict[str, Any],
    ) -> Optional[BusMessage]:
        """
        接收消息（通过适配器转换）
        
        Args:
            raw_message: 平台原始消息
        
        Returns:
            BusMessage v3，如果无效返回 None
        """
        if not self.adapter:
            logger.warning("No adapter configured for channel %s", self.channel)
            return None
        
        # 验证消息
        if not self.adapter.validate_message(raw_message):
            logger.warning("Invalid message for channel %s", self.channel)
            return None
        
        # 转换为 BusMessage v3
        bus_message = await self.adapter.convert_to_bus_message(raw_message)
        
        # 注入 SessionContext（可选）
        await self._inject_session_context(bus_message)
        
        return bus_message
    
    async def send_message(
        self,
        message: BusMessage,
    ) -> bool:
        """
        发送消息（通过适配器转换）
        
        Args:
            message: BusMessage v3
        
        Returns:
            是否成功
        """
        if not self.adapter:
            logger.warning("No adapter configured for channel %s", self.channel)
            return False
        
        # 转换为平台消息
        platform_message = await self.adapter.convert_from_bus_message(message)
        
        # 发送到平台（子类实现）
        return await self._send_to_platform(platform_message)
    
    async def _inject_session_context(
        self,
        message: BusMessage,
    ):
        """
        注入 SessionContext
        
        Args:
            message: BusMessage v3
        """
        # 从六层标识符构建 SessionContext
        session_context = SessionContext(
            channel=message.channel_id,
            caller_logical_id=message.caller_logical_id,
            caller_physical_id=message.caller_physical_id,
            called_id=message.called_id,
            session_id=message.session_id,
        )
        
        # 存储到 meta 字段（BusMessage 无 session_context 字段）
        if message.meta is None:
            message.meta = {}
        message.meta["session_context"] = session_context
        
        logger.debug(
            "Injected session context: channel=%s, caller=%s, called=%s, session=%s",
            message.channel_id,
            message.caller_logical_id,
            message.called_id,
            message.session_id,
        )
    
    async def _send_to_platform(
        self,
        platform_message: Dict[str, Any],
    ) -> bool:
        """
        发送到平台（子类实现）
        
        Args:
            platform_message: 平台消息格式
        
        Returns:
            是否成功
        """
        # 默认实现：记录日志
        logger.info(
            "Sending to platform %s: %s",
            self.channel,
            platform_message,
        )
        return True
    
    def resolve_session_id(
        self,
        sender_id: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        解析 session_id（兼容旧版）
        
        Args:
            sender_id: 发送者 ID
            meta: 元数据
        
        Returns:
            session_id
        """
        if meta and "session_id" in meta:
            return meta["session_id"]
        
        # 默认使用 sender_id 作为 session_id
        return f"sess_{sender_id}"


# 导出时兼容旧版
BaseChannel = BaseChannelV2
