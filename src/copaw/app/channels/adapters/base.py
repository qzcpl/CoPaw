"""
基础适配器

定义适配器接口，所有平台适配器继承此类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

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


class BaseAdapter(ABC):
    """
    基础适配器
    
    定义平台消息与 BusMessage v3 之间的转换接口
    
    子类实现：
    1. convert_to_bus_message - 平台消息 → BusMessage v3
    2. convert_from_bus_message - BusMessage v3 → 平台消息
    """
    
    # 平台标识
    PLATFORM_ID: str = "unknown"
    
    # 平台能力
    SUPPORTS_MARKDOWN: bool = True
    SUPPORTS_IMAGE: bool = True
    SUPPORTS_FILE: bool = True
    SUPPORTS_VOICE: bool = False
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Args:
            config: 适配器配置
        """
        self.config = config or {}
        self._init_config()
    
    def _init_config(self):
        """初始化配置（子类可重写）"""
        pass
    
    @abstractmethod
    async def convert_to_bus_message(
        self,
        raw_message: Dict[str, Any],
    ) -> BusMessage:
        """
        将平台原始消息转换为 BusMessage v3
        
        Args:
            raw_message: 平台原始消息
        
        Returns:
            BusMessage v3（含六层标识符和 SessionContext）
        
        转换逻辑：
        1. 提取六层标识符
        2. 转换消息内容
        3. 生成 message_id
        4. 设置 SessionContext（可选）
        """
        pass
    
    @abstractmethod
    async def convert_from_bus_message(
        self,
        message: BusMessage,
    ) -> Dict[str, Any]:
        """
        将 BusMessage v3 转换为平台消息格式
        
        Args:
            message: BusMessage v3
        
        Returns:
            平台消息格式
        
        转换逻辑：
        1. 提取内容
        2. 转换为平台格式
        3. 添加平台特定字段
        """
        pass
    
    def _extract_six_layer_id(
        self,
        raw_message: Dict[str, Any],
    ) -> Identifiers:
        """
        从原始消息提取六层标识符
        
        子类根据平台特性实现
        
        Args:
            raw_message: 平台原始消息
        
        Returns:
            Identifiers
        """
        # 默认实现：从配置或消息中提取
        return Identifiers(
            channel_id=ChannelId(self.PLATFORM_ID),
            caller_logical_id=CallerLogicalId(
                f"user_{raw_message.get('sender_id', 'unknown')}",
                caller_type=CallerType.USER,
            ),
            caller_physical_id=CallerPhysicalId(
                f"user_{raw_message.get('sender_id', 'unknown')}",
            ),
            called_id=CalledId(self.config.get("called_id", "default")),
            session_id=SessionId(raw_message.get("session_id", self._generate_session_id())),
            message_id=MessageId(raw_message.get("message_id", self._generate_message_id())),
            channel_type="private",
        )
    
    def _generate_message_id(self) -> str:
        """生成 message_id"""
        import uuid
        return f"msg_{uuid.uuid4().hex[:16]}"
    
    def _generate_session_id(self) -> str:
        """生成 session_id"""
        import uuid
        return f"sess_{uuid.uuid4().hex[:16]}"
    
    def _convert_content_type(
        self,
        raw_type: str,
    ) -> str:
        """
        转换内容类型
        
        Args:
            raw_type: 平台内容类型
        
        Returns:
            标准内容类型（text/image/file/voice）
        """
        type_mapping = {
            "text": "text",
            "txt": "text",
            "image": "image",
            "img": "image",
            "file": "file",
            "audio": "voice",
            "voice": "voice",
        }
        return type_mapping.get(raw_type.lower(), "text")
    
    def _parse_timestamp(
        self,
        timestamp: Any,
    ) -> datetime:
        """
        解析时间戳
        
        Args:
            timestamp: 平台时间戳
        
        Returns:
            datetime 对象
        """
        if isinstance(timestamp, datetime):
            return timestamp
        
        if isinstance(timestamp, (int, float)):
            # 秒级时间戳
            if timestamp > 1e12:
                # 毫秒级
                return datetime.fromtimestamp(timestamp / 1000)
            else:
                return datetime.fromtimestamp(timestamp)
        
        if isinstance(timestamp, str):
            # ISO 格式
            try:
                return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                pass
        
        # 默认返回当前时间
        return datetime.now()
    
    def validate_message(
        self,
        raw_message: Dict[str, Any],
    ) -> bool:
        """
        验证消息有效性
        
        Args:
            raw_message: 平台原始消息
        
        Returns:
            是否有效
        """
        # 基本验证
        if not isinstance(raw_message, dict):
            return False
        
        # 子类可添加额外验证
        return True
