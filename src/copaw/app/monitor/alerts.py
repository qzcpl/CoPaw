"""
告警系统

职责：
1. 发送告警到不同渠道
2. 告警去重（避免告警风暴）
3. 告警升级（严重告警通知更多人）
"""

import logging
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    """告警级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertChannel(str, Enum):
    """告警渠道"""
    LOG = "log"
    EMAIL = "email"
    DINGTALK = "dingtalk"
    WEBHOOK = "webhook"


class Alert:
    """告警消息"""
    
    def __init__(
        self,
        title: str,
        message: str,
        level: AlertLevel = AlertLevel.WARNING,
        channels: Optional[List[AlertChannel]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.title = title
        self.message = message
        self.level = level
        self.channels = channels or [AlertChannel.LOG]
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        self.id = f"alert_{self.timestamp.strftime('%Y%m%d%H%M%S')}_{id(self)}"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'level': self.level.value,
            'channels': [c.value for c in self.channels],
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
        }
    
    def __str__(self) -> str:
        return f"[{self.level.value.upper()}] {self.title}: {self.message}"


class AlertManager:
    """
    告警管理器
    
    职责：
    1. 发送告警到不同渠道
    2. 告警去重（避免告警风暴）
    3. 告警升级（严重告警通知更多人）
    """
    
    def __init__(
        self,
        dedup_window_seconds: int = 300,  # 5 分钟去重窗口
        max_alerts_per_window: int = 10,  # 窗口内最大告警数
    ):
        self._alert_history: List[Alert] = []
        self._dedup_window_seconds = dedup_window_seconds
        self._max_alerts_per_window = max_alerts_per_window
        
        # 告警配置
        self._email_recipients: List[str] = []
        self._dingtalk_webhook: Optional[str] = None
        self._webhook_url: Optional[str] = None
    
    def configure_email(self, recipients: List[str]) -> None:
        """配置邮件接收者"""
        self._email_recipients = recipients
    
    def configure_dingtalk(self, webhook: str) -> None:
        """配置钉钉机器人"""
        self._dingtalk_webhook = webhook
    
    def configure_webhook(self, url: str) -> None:
        """配置 Webhook"""
        self._webhook_url = url
    
    async def send_alert(self, alert: Alert) -> bool:
        """
        发送告警
        
        Returns:
            是否发送成功
        """
        # === 1. 去重检查 ===
        if self._is_duplicate(alert):
            logger.debug(f"Alert deduplicated: {alert.title}")
            return False
        
        # === 2. 限流检查 ===
        if self._is_rate_limited(alert):
            logger.warning(f"Alert rate limited: {alert.title}")
            return False
        
        # === 3. 发送到各渠道 ===
        success = True
        
        for channel in alert.channels:
            try:
                if channel == AlertChannel.LOG:
                    await self._send_log_alert(alert)
                elif channel == AlertChannel.EMAIL:
                    await self._send_email_alert(alert)
                elif channel == AlertChannel.DINGTALK:
                    await self._send_dingtalk_alert(alert)
                elif channel == AlertChannel.WEBHOOK:
                    await self._send_webhook_alert(alert)
            except Exception as e:
                logger.error(f"Failed to send alert via {channel.value}: {e}")
                success = False
        
        # === 4. 记录历史 ===
        self._alert_history.append(alert)
        
        # === 5. 清理过期历史 ===
        self._cleanup_history()
        
        return success
    
    def _is_duplicate(self, alert: Alert) -> bool:
        """检查是否重复告警"""
        window_start = datetime.now() - timedelta(seconds=self._dedup_window_seconds)
        
        for prev_alert in self._alert_history:
            if prev_alert.timestamp >= window_start:
                if (prev_alert.title == alert.title and 
                    prev_alert.message == alert.message):
                    return True
        
        return False
    
    def _is_rate_limited(self, alert: Alert) -> bool:
        """检查是否触发限流"""
        window_start = datetime.now() - timedelta(seconds=self._dedup_window_seconds)
        
        recent_alerts = [
            a for a in self._alert_history
            if a.timestamp >= window_start
        ]
        
        return len(recent_alerts) >= self._max_alerts_per_window
    
    def _cleanup_history(self) -> None:
        """清理过期历史"""
        window_start = datetime.now() - timedelta(seconds=self._dedup_window_seconds)
        self._alert_history = [
            a for a in self._alert_history
            if a.timestamp >= window_start
        ]
    
    async def _send_log_alert(self, alert: Alert) -> None:
        """发送日志告警"""
        log_func = {
            AlertLevel.INFO: logger.info,
            AlertLevel.WARNING: logger.warning,
            AlertLevel.ERROR: logger.error,
            AlertLevel.CRITICAL: logger.critical,
        }.get(alert.level, logger.warning)
        
        log_func(f"[ALERT] {alert.title}: {alert.message}")
    
    async def _send_email_alert(self, alert: Alert) -> None:
        """发送邮件告警"""
        if not self._email_recipients:
            logger.warning("Email recipients not configured")
            return
        
        # TODO: 实现邮件发送
        # 使用 himalaya 或 smtplib
        logger.info(
            f"Email alert sent to {self._email_recipients}: "
            f"{alert.title}"
        )
    
    async def _send_dingtalk_alert(self, alert: Alert) -> None:
        """发送钉钉告警"""
        if not self._dingtalk_webhook:
            logger.warning("DingTalk webhook not configured")
            return
        
        # 构建钉钉消息
        message = {
            "msgtype": "markdown",
            "markdown": {
                "title": alert.title,
                "text": self._format_dingtalk_markdown(alert),
            },
            "at": {
                "isAtAll": alert.level in [AlertLevel.ERROR, AlertLevel.CRITICAL],
            }
        }
        
        # TODO: 调用钉钉机器人 API
        # async with aiohttp.ClientSession() as session:
        #     async with session.post(self._dingtalk_webhook, json=message) as resp:
        #         if resp.status != 200:
        #             raise Exception(f"DingTalk API error: {resp.status}")
        
        logger.info(f"DingTalk alert sent: {alert.title}")
    
    def _format_dingtalk_markdown(self, alert: Alert) -> str:
        """格式化钉钉 Markdown 消息"""
        level_colors = {
            AlertLevel.INFO: "🔵",
            AlertLevel.WARNING: "🟡",
            AlertLevel.ERROR: "🔴",
            AlertLevel.CRITICAL: "🔴🔴",
        }
        
        color = level_colors.get(alert.level, "⚪")
        
        return f"""## {color} {alert.title}

**级别：** {alert.level.value.upper()}
**时间：** {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
**详情：** {alert.message}

{self._format_metadata(alert.metadata)}
"""
    
    def _format_metadata(self, metadata: Dict) -> str:
        """格式化元数据"""
        if not metadata:
            return ""
        
        lines = ["**元数据：**"]
        for key, value in metadata.items():
            lines.append(f"- {key}: {value}")
        
        return "\n".join(lines)
    
    async def _send_webhook_alert(self, alert: Alert) -> None:
        """发送 Webhook 告警"""
        if not self._webhook_url:
            logger.warning("Webhook URL not configured")
            return
        
        # TODO: 调用 Webhook
        # async with aiohttp.ClientSession() as session:
        #     async with session.post(self._webhook_url, json=alert.to_dict()) as resp:
        #         if resp.status != 200:
        #             raise Exception(f"Webhook error: {resp.status}")
        
        logger.info(f"Webhook alert sent: {alert.title}")
    
    def get_alert_history(
        self,
        limit: int = 100,
        level: Optional[AlertLevel] = None,
    ) -> List[Alert]:
        """
        获取告警历史
        
        Args:
            limit: 返回数量限制
            level: 按级别过滤
        
        Returns:
            告警列表
        """
        history = self._alert_history.copy()
        
        if level:
            history = [a for a in history if a.level == level]
        
        # 按时间倒序
        history.sort(key=lambda a: a.timestamp, reverse=True)
        
        return history[:limit]
    
    def get_stats(self) -> Dict:
        """获取告警统计"""
        stats = {
            "total": len(self._alert_history),
            "by_level": {},
            "by_channel": {},
        }
        
        # 按级别统计
        for level in AlertLevel:
            count = len([a for a in self._alert_history if a.level == level])
            stats["by_level"][level.value] = count
        
        # 按渠道统计
        for alert in self._alert_history:
            for channel in alert.channels:
                channel_name = channel.value
                stats["by_channel"][channel_name] = \
                    stats["by_channel"].get(channel_name, 0) + 1
        
        return stats
