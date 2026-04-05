"""
消息队列基类

定义队列的统一接口
支持多种后端实现：Redis、SQLite、内存
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Any
from datetime import datetime

from copaw.app.channels.schema import BusMessage


class BaseQueue(ABC):
    """
    消息队列基类
    
    定义队列的统一接口
    支持多种后端实现：Redis、SQLite、内存
    
    Attributes:
        name: 队列名称
        max_retries: 最大重试次数
    """
    
    def __init__(self, name: str, max_retries: int = 3):
        self.name = name
        self.max_retries = max_retries
    
    @abstractmethod
    async def enqueue(self, message: BusMessage) -> bool:
        """
        入队消息
        
        Args:
            message: BusMessage
        
        Returns:
            是否成功
        """
        pass
    
    @abstractmethod
    async def dequeue(self, timeout: float = 0) -> Optional[BusMessage]:
        """
        出队消息
        
        Args:
            timeout: 超时时间（0 表示不等待）
        
        Returns:
            BusMessage，队列为空返回 None
        """
        pass
    
    @abstractmethod
    async def peek(self) -> Optional[BusMessage]:
        """
        查看队首消息（不出队）
        """
        pass
    
    @abstractmethod
    async def size(self) -> int:
        """
        队列长度
        """
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """
        清空队列
        """
        pass
    
    @abstractmethod
    async def persist(self) -> bool:
        """
        持久化队列到磁盘
        
        用于关机前保存
        """
        pass
    
    @abstractmethod
    async def restore(self) -> bool:
        """
        从磁盘恢复队列
        
        用于启动时恢复
        """
        pass
    
    @abstractmethod
    async def acknowledge(self, message_id: str) -> bool:
        """
        确认消息处理成功
        
        Args:
            message_id: 消息 ID
        
        Returns:
            是否成功
        """
        pass
    
    @abstractmethod
    async def fail(
        self,
        message_id: str,
        error_message: str,
    ) -> bool:
        """
        标记消息处理失败
        
        Args:
            message_id: 消息 ID
            error_message: 错误信息
        
        Returns:
            是否成功
        """
        pass
    
    @abstractmethod
    async def requeue(
        self,
        message: BusMessage,
        reason: str = "",
    ) -> bool:
        """
        重新入队（失败重试）
        
        Args:
            message: 消息
            reason: 重试原因
        
        Returns:
            是否成功
        """
        pass
