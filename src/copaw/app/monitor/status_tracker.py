"""
状态追踪器

职责：
1. 追踪消息状态变更
2. 记录状态变更日志
3. 提供状态查询接口
4. 生成统计报表

消息状态流转：
received → dispatched → processing → completed
                                       ↓
                                    failed/timeout
"""

import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class MessageStatus(str, Enum):
    """消息状态"""
    RECEIVED = "received"
    DISPATCHED = "dispatched"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    RETRYING = "retrying"


class SessionStatus(str, Enum):
    """会话状态"""
    ACTIVE = "active"
    IDLE = "idle"
    TIMEOUT = "timeout"
    CLOSED = "closed"


class StatusTracker:
    """
    状态追踪器
    
    职责：
    1. 追踪消息状态变更
    2. 记录状态变更日志
    3. 提供状态查询接口
    4. 生成统计报表
    """
    
    def __init__(self):
        # 内存存储（生产环境应使用数据库）
        self._message_states: Dict[str, Dict] = {}
        self._session_states: Dict[str, Dict] = {}
        self._status_logs: List[Dict] = []
        
        # 统计
        self._stats = {
            "total_messages": 0,
            "completed": 0,
            "failed": 0,
            "timeout": 0,
            "total_processing_time_ms": 0,
        }
    
    async def track_status_change(
        self,
        object_type: str,           # message/session
        object_id: str,
        old_status: Optional[str],
        new_status: str,
        reason: Optional[str] = None,
        operator: str = "system",
        metadata: Optional[Dict] = None,
    ) -> None:
        """
        追踪状态变更
        
        Args:
            object_type: 对象类型（message/session）
            object_id: 对象 ID
            old_status: 旧状态
            new_status: 新状态
            reason: 变更原因
            operator: 操作人
            metadata: 元数据
        """
        logger.info(
            f"Status change: {object_type}/{object_id} "
            f"{old_status} -> {new_status}"
        )
        
        # === 1. 记录状态变更日志 ===
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "object_type": object_type,
            "object_id": object_id,
            "old_status": old_status,
            "new_status": new_status,
            "reason": reason,
            "operator": operator,
            "metadata": metadata or {},
        }
        self._status_logs.append(log_entry)
        
        # === 2. 更新对象状态 ===
        if object_type == "message":
            await self._update_message_status(object_id, new_status, metadata)
        elif object_type == "session":
            await self._update_session_status(object_id, new_status, metadata)
    
    async def _update_message_status(
        self,
        message_id: str,
        status: str,
        metadata: Optional[Dict] = None,
    ) -> None:
        """更新消息状态"""
        now = datetime.now()
        
        if message_id not in self._message_states:
            self._message_states[message_id] = {
                "message_id": message_id,
                "status": status,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "history": [],
                "metadata": metadata or {},
            }
        else:
            state = self._message_states[message_id]
            state["status"] = status
            state["updated_at"] = now.isoformat()
            state["metadata"].update(metadata or {})
        
        # 添加到历史记录
        self._message_states[message_id]["history"].append({
            "status": status,
            "timestamp": now.isoformat(),
        })
        
        # 更新统计
        self._update_message_stats(status, metadata)
    
    async def _update_session_status(
        self,
        session_id: str,
        status: str,
        metadata: Optional[Dict] = None,
    ) -> None:
        """更新会话状态"""
        now = datetime.now()
        
        if session_id not in self._session_states:
            self._session_states[session_id] = {
                "session_id": session_id,
                "status": status,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "history": [],
                "metadata": metadata or {},
            }
        else:
            state = self._session_states[session_id]
            state["status"] = status
            state["updated_at"] = now.isoformat()
            state["metadata"].update(metadata or {})
        
        # 添加到历史记录
        self._session_states[session_id]["history"].append({
            "status": status,
            "timestamp": now.isoformat(),
        })
    
    def _update_message_stats(
        self,
        status: str,
        metadata: Optional[Dict],
    ) -> None:
        """更新消息统计"""
        self._stats["total_messages"] += 1
        
        if status == MessageStatus.COMPLETED:
            self._stats["completed"] += 1
            
            # 计算处理时间
            if metadata and "processing_time_ms" in metadata:
                self._stats["total_processing_time_ms"] += \
                    metadata["processing_time_ms"]
        
        elif status == MessageStatus.FAILED:
            self._stats["failed"] += 1
        
        elif status == MessageStatus.TIMEOUT:
            self._stats["timeout"] += 1
    
    async def get_message_status(
        self,
        message_id: str,
    ) -> Optional[Dict]:
        """
        获取消息状态
        
        Returns:
            {
                status: str,
                updated_at: datetime,
                history: [状态变更历史]
            }
        """
        return self._message_states.get(message_id)
    
    async def get_session_status(
        self,
        session_id: str,
    ) -> Optional[Dict]:
        """获取会话状态"""
        return self._session_states.get(session_id)
    
    async def get_status_history(
        self,
        object_type: str,
        object_id: str,
        limit: int = 50,
    ) -> List[Dict]:
        """
        获取状态变更历史
        
        Returns:
            [
                {
                    old_status: str,
                    new_status: str,
                    reason: str,
                    operator: str,
                    timestamp: str,
                }
            ]
        """
        history = [
            log for log in self._status_logs
            if log["object_type"] == object_type and log["object_id"] == object_id
        ]
        
        # 按时间倒序
        history.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return history[:limit]
    
    async def get_stats(
        self,
        time_range: str = "1h",      # 1h/24h/7d
    ) -> Dict:
        """
        获取统计报表
        
        Returns:
            {
                total_messages: int,
                completed: int,
                failed: int,
                timeout: int,
                avg_processing_time_ms: float,
            }
        """
        avg_processing_time = 0
        if self._stats["completed"] > 0:
            avg_processing_time = \
                self._stats["total_processing_time_ms"] / self._stats["completed"]
        
        return {
            "total_messages": self._stats["total_messages"],
            "completed": self._stats["completed"],
            "failed": self._stats["failed"],
            "timeout": self._stats["timeout"],
            "avg_processing_time_ms": avg_processing_time,
            "success_rate": self._calculate_success_rate(),
        }
    
    def _calculate_success_rate(self) -> float:
        """计算成功率"""
        total = self._stats["total_messages"]
        if total == 0:
            return 0.0
        
        return self._stats["completed"] / total * 100
    
    async def cleanup_old_data(
        self,
        retention_days: int = 7,
    ) -> int:
        """
        清理旧数据
        
        Args:
            retention_days: 保留天数
        
        Returns:
            清理的记录数
        """
        cutoff = datetime.now() - timedelta(days=retention_days)
        
        # 清理状态日志
        original_count = len(self._status_logs)
        self._status_logs = [
            log for log in self._status_logs
            if datetime.fromisoformat(log["timestamp"]) >= cutoff
        ]
        cleaned_logs = original_count - len(self._status_logs)
        
        # 清理消息状态（只保留最近的）
        # 简化实现：不清理，生产环境应实现 LRU 或归档
        
        logger.info(f"Cleaned up {cleaned_logs} old status logs")
        return cleaned_logs
