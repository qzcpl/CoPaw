"""
监控模块测试

测试 TimeoutDetector、AlertManager、StatusTracker
"""

import pytest
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加补丁目录到路径
patch_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(patch_src))

from copaw.app.monitor.timeout_detector import TimeoutDetector
from copaw.app.monitor.alerts import AlertManager, Alert, AlertLevel, AlertChannel
from copaw.app.monitor.status_tracker import (
    StatusTracker,
    MessageStatus,
    SessionStatus,
)


class TestAlertManager:
    """告警管理器测试"""
    
    @pytest.fixture
    def alert_manager(self):
        """创建告警管理器"""
        return AlertManager(
            dedup_window_seconds=60,
            max_alerts_per_window=10,
        )
    
    @pytest.mark.asyncio
    async def test_send_log_alert(self, alert_manager):
        """测试日志告警"""
        alert = Alert(
            title="测试告警",
            message="这是一条测试告警消息",
            level=AlertLevel.WARNING,
            channels=[AlertChannel.LOG],
        )
        
        result = await alert_manager.send_alert(alert)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_alert_deduplication(self, alert_manager):
        """测试告警去重"""
        alert1 = Alert(
            title="测试告警",
            message="相同消息",
            level=AlertLevel.WARNING,
        )
        
        # 第一次发送成功
        result1 = await alert_manager.send_alert(alert1)
        assert result1 is True
        
        # 第二次发送（重复）应该失败
        alert2 = Alert(
            title="测试告警",
            message="相同消息",
            level=AlertLevel.WARNING,
        )
        result2 = await alert_manager.send_alert(alert2)
        assert result2 is False
    
    @pytest.mark.asyncio
    async def test_alert_history(self, alert_manager):
        """测试告警历史"""
        alerts = []
        for i in range(5):
            alert = Alert(
                title=f"告警{i}",
                message=f"消息{i}",
                level=AlertLevel.INFO,
            )
            await alert_manager.send_alert(alert)
            alerts.append(alert)
        
        history = alert_manager.get_alert_history()
        
        assert len(history) == 5
        # 最新在前（告警编号从 0-4）
        assert "告警" in history[0].title
    
    @pytest.mark.asyncio
    async def test_alert_stats(self, alert_manager):
        """测试告警统计"""
        # 发送不同级别的告警
        await alert_manager.send_alert(Alert("告警 1", "msg", AlertLevel.INFO))
        await alert_manager.send_alert(Alert("告警 2", "msg", AlertLevel.WARNING))
        await alert_manager.send_alert(Alert("告警 3", "msg", AlertLevel.ERROR))
        
        stats = alert_manager.get_stats()
        
        assert stats["total"] == 3
        assert stats["by_level"]["info"] == 1
        assert stats["by_level"]["warning"] == 1
        assert stats["by_level"]["error"] == 1
    
    @pytest.mark.asyncio
    async def test_alert_to_dict(self, alert_manager):
        """测试告警序列化"""
        alert = Alert(
            title="测试",
            message="消息",
            level=AlertLevel.CRITICAL,
            metadata={"key": "value"},
        )
        
        data = alert.to_dict()
        
        assert data["title"] == "测试"
        assert data["level"] == "critical"
        assert data["metadata"]["key"] == "value"
        assert "timestamp" in data


class TestStatusTracker:
    """状态追踪器测试"""
    
    @pytest.fixture
    def tracker(self):
        """创建状态追踪器"""
        return StatusTracker()
    
    @pytest.mark.asyncio
    async def test_track_message_status(self, tracker):
        """测试消息状态追踪"""
        await tracker.track_status_change(
            object_type="message",
            object_id="msg_001",
            old_status=None,
            new_status=MessageStatus.RECEIVED,
            operator="system",
        )
        
        status = await tracker.get_message_status("msg_001")
        
        assert status is not None
        assert status["status"] == MessageStatus.RECEIVED
    
    @pytest.mark.asyncio
    async def test_status_history(self, tracker):
        """测试状态历史"""
        # 多次状态变更
        await tracker.track_status_change(
            "message", "msg_001", None, MessageStatus.RECEIVED,
        )
        await tracker.track_status_change(
            "message", "msg_001", MessageStatus.RECEIVED, MessageStatus.PROCESSING,
        )
        await tracker.track_status_change(
            "message", "msg_001", MessageStatus.PROCESSING, MessageStatus.COMPLETED,
        )
        
        history = await tracker.get_status_history("message", "msg_001")
        
        assert len(history) == 3
        assert history[0]["new_status"] == MessageStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_session_status(self, tracker):
        """测试会话状态"""
        await tracker.track_status_change(
            object_type="session",
            object_id="sess_001",
            old_status=None,
            new_status=SessionStatus.ACTIVE,
        )
        
        status = await tracker.get_session_status("sess_001")
        
        assert status is not None
        assert status["status"] == SessionStatus.ACTIVE
    
    @pytest.mark.asyncio
    async def test_stats(self, tracker):
        """测试统计"""
        # 模拟消息处理
        await tracker.track_status_change(
            "message", "msg_1", None, MessageStatus.COMPLETED,
            metadata={"processing_time_ms": 100},
        )
        await tracker.track_status_change(
            "message", "msg_2", None, MessageStatus.COMPLETED,
            metadata={"processing_time_ms": 200},
        )
        await tracker.track_status_change(
            "message", "msg_3", None, MessageStatus.FAILED,
        )
        
        stats = await tracker.get_stats()
        
        assert stats["total_messages"] == 3
        assert stats["completed"] == 2
        assert stats["failed"] == 1
        assert stats["avg_processing_time_ms"] == 150
        assert stats["success_rate"] == pytest.approx(66.67, rel=0.1)
    
    @pytest.mark.asyncio
    async def test_nonexistent_message(self, tracker):
        """测试不存在的消息"""
        status = await tracker.get_message_status("nonexistent")
        assert status is None


class TestTimeoutDetector:
    """超时检测器测试"""
    
    @pytest.fixture
    def detector(self):
        """创建超时检测器"""
        return TimeoutDetector(
            message_timeout_seconds=60,
            session_timeout_seconds=300,
            scan_interval_seconds=10,
        )
    
    def test_check_message_timeout(self, detector):
        """测试消息超时检查"""
        # 创建消息
        from copaw.app.channels.schema import BusMessage
        
        # 未超时消息
        msg1 = BusMessage(
            message_id="msg_1",
            channel_id="test",
            caller_logical_id="user_1",
            caller_physical_id="user_1",
            called_id="agent_1",
            session_id="sess_1",
            channel_type="private",
            content="test",
            meta={"created_at": datetime.now().isoformat()},
        )
        
        # 超时消息（手动设置旧时间）
        msg2 = BusMessage(
            message_id="msg_2",
            channel_id="test",
            caller_logical_id="user_1",
            caller_physical_id="user_1",
            called_id="agent_1",
            session_id="sess_1",
            channel_type="private",
            content="test",
            meta={"created_at": (datetime.now() - timedelta(minutes=5)).isoformat()},
        )
        
        assert detector.check_message_timeout(msg1) is False
        assert detector.check_message_timeout(msg2) is True
    
    def test_get_stats(self, detector):
        """测试获取统计"""
        stats = detector.get_stats()
        
        assert "messages_timeout" in stats
        assert "sessions_timeout" in stats
        assert "queue_alerts" in stats
    
    @pytest.mark.asyncio
    async def test_start_stop(self, detector):
        """测试启动停止"""
        await detector.start()
        assert detector._running is True
        
        await asyncio.sleep(0.1)
        
        await detector.stop()
        assert detector._running is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
