"""
超时检测器

职责：
1. 定期扫描超时消息
2. 触发超时处理
3. 发送告警
4. 记录超时日志

超时策略：
- 消息处理超时（默认 5 分钟）
- 会话空闲超时（默认 30 分钟）
- 队列积压告警（默认 1000 条）
"""

import logging
import asyncio
from typing import Optional, Dict, List, Callable, Awaitable, TYPE_CHECKING
from datetime import datetime, timedelta

if TYPE_CHECKING:
    from copaw.app.channels.schema import BusMessage

logger = logging.getLogger(__name__)


class TimeoutDetector:
    """
    超时检测器
    
    职责：
    1. 定期扫描超时消息
    2. 触发超时处理
    3. 发送告警
    4. 记录超时日志
    """
    
    def __init__(
        self,
        message_timeout_seconds: int = 300,      # 5 分钟
        session_timeout_seconds: int = 1800,     # 30 分钟
        queue_threshold: int = 1000,             # 积压告警阈值
        scan_interval_seconds: int = 60,         # 扫描间隔
    ):
        self.message_timeout_seconds = message_timeout_seconds
        self.session_timeout_seconds = session_timeout_seconds
        self.queue_threshold = queue_threshold
        self.scan_interval_seconds = scan_interval_seconds
        
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
        # 超时回调
        self._on_message_timeout: Optional[Callable] = None
        self._on_session_timeout: Optional[Callable] = None
        self._on_queue_alert: Optional[Callable] = None
        
        # 统计
        self._stats = {
            "messages_timeout": 0,
            "sessions_timeout": 0,
            "queue_alerts": 0,
        }
    
    def set_message_timeout_handler(
        self,
        handler: Callable,
    ) -> None:
        """设置消息超时处理器"""
        self._on_message_timeout = handler
    
    def set_session_timeout_handler(
        self,
        handler: Callable,
    ) -> None:
        """设置会话超时处理器"""
        self._on_session_timeout = handler
    
    def set_queue_alert_handler(
        self,
        handler: Callable,
    ) -> None:
        """设置队列告警处理器"""
        self._on_queue_alert = handler
    
    async def start(self) -> None:
        """启动超时检测"""
        if self._running:
            logger.warning("TimeoutDetector already running")
            return
        
        self._running = True
        self._task = asyncio.create_task(self._scan_loop())
        logger.info(f"TimeoutDetector started (interval={self.scan_interval_seconds}s)")
    
    async def stop(self) -> None:
        """停止超时检测"""
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        logger.info("TimeoutDetector stopped")
    
    async def _scan_loop(self) -> None:
        """扫描循环"""
        while self._running:
            try:
                await self._scan()
                await asyncio.sleep(self.scan_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"TimeoutDetector scan error: {e}")
                await asyncio.sleep(self.scan_interval_seconds)
    
    async def _scan(self) -> None:
        """
        执行扫描
        
        检查项：
        1. 超时消息
        2. 超时会话
        3. 队列积压
        """
        logger.debug("TimeoutDetector scanning...")
        
        # === 1. 扫描超时消息 ===
        # 从数据库或缓存中查询超时消息
        timeout_messages = await self._scan_timeout_messages()
        for msg in timeout_messages:
            await self._handle_message_timeout(msg)
        
        # === 2. 扫描超时会话 ===
        timeout_sessions = await self._scan_timeout_sessions()
        for session_id in timeout_sessions:
            await self._handle_session_timeout(session_id)
        
        # === 3. 检查队列积压 ===
        # 需要传入 queue_manager
        # queue_size = await queue_manager.get_queue_size('default')
        # if queue_size > self.queue_threshold:
        #     await self._handle_queue_alert('default', queue_size)
        
        logger.debug("TimeoutDetector scan completed")
    
    async def _scan_timeout_messages(self) -> List:
        """扫描超时消息"""
        # TODO: 从数据库查询超时消息
        # 这里返回空列表，实际实现需要查询数据库
        return []
    
    async def _scan_timeout_sessions(self) -> List[str]:
        """扫描超时会话"""
        # TODO: 从数据库查询超时会话
        return []
    
    async def _handle_message_timeout(self, message) -> None:
        """处理消息超时"""
        logger.warning(
            f"Message timeout: {message.message_id}, "
            f"session={message.session_id}, "
            f"timeout={self.message_timeout_seconds}s"
        )
        
        # 更新统计
        self._stats["messages_timeout"] += 1
        
        # 调用处理器
        if self._on_message_timeout:
            await self._on_message_timeout(message)
    
    async def _handle_session_timeout(self, session_id: str) -> None:
        """处理会话超时"""
        logger.warning(f"Session timeout: {session_id}")
        
        # 更新统计
        self._stats["sessions_timeout"] += 1
        
        # 调用处理器
        if self._on_session_timeout:
            await self._on_session_timeout(session_id)
    
    async def _handle_queue_alert(
        self,
        queue_name: str,
        size: int,
    ) -> None:
        """处理队列积压告警"""
        logger.warning(
            f"Queue backlog alert: {queue_name}, size={size}, "
            f"threshold={self.queue_threshold}"
        )
        
        # 更新统计
        self._stats["queue_alerts"] += 1
        
        # 调用处理器
        if self._on_queue_alert:
            await self._on_queue_alert(queue_name, size)
    
    def check_message_timeout(
        self,
        message,
    ) -> bool:
        """
        检查单条消息是否超时
        
        Returns:
            是否超时
        """
        if not message.meta:
            return False
        
        created_at = message.meta.get("created_at")
        if not created_at:
            return False
        
        # 解析时间戳
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at).timestamp()
            except:
                return False
        
        now = datetime.now().timestamp()
        is_timeout = (now - created_at) > self.message_timeout_seconds
        
        if is_timeout:
            logger.warning(
                f"Message timeout detected: {message.message_id}"
            )
        
        return is_timeout
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self._stats.copy()
