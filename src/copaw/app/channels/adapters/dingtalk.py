"""
钉钉适配器

实现钉钉消息与 BusMessage v3 之间的转换
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

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

from .base import BaseAdapter


class DingTalkAdapter(BaseAdapter):
    """
    钉钉适配器
    
    支持消息类型：
    - text: 文本消息
    - markdown: Markdown 消息
    - image: 图片消息
    - file: 文件消息
    - link: 链接消息
    
    六层标识符映射：
    - channel_id: "dingtalk"
    - caller_logical_id: conversation_id（群聊/私聊 ID）
    - caller_physical_id: sender_id（发送者 ID）
    - called_id: robot_code（机器人 ID）
    - session_id: 从 conversation_id 生成
    - message_id: messageId（钉钉消息 ID）
    """
    
    PLATFORM_ID = "dingtalk"
    SUPPORTS_MARKDOWN = True
    SUPPORTS_IMAGE = True
    SUPPORTS_FILE = True
    SUPPORTS_VOICE = False
    
    def _init_config(self):
        """初始化配置"""
        self.robot_code = self.config.get("robot_code", "")
        self.media_dir = self.config.get("media_dir", "")
    
    async def convert_to_bus_message(
        self,
        raw_message: Dict[str, Any],
    ) -> BusMessage:
        """
        钉钉消息 → BusMessage v3
        
        Args:
            raw_message: 钉钉原始消息（ChatbotMessage 或 dict）
        
        Returns:
            BusMessage v3
        """
        # 提取六层标识符
        six_layer_id = self._extract_six_layer_id(raw_message)
        
        # 提取消息内容
        content = self._extract_content(raw_message)
        content_type = self._extract_content_type(raw_message)
        
        # 提取时间戳
        timestamp = self._extract_timestamp(raw_message)
        
        # 创建 BusMessage v3
        return BusMessage(
            message_id=str(six_layer_id.message_id),
            channel_id=str(six_layer_id.channel_id),
            caller_logical_id=str(six_layer_id.caller_logical_id),
            caller_physical_id=str(six_layer_id.caller_physical_id),
            called_id=str(six_layer_id.called_id),
            session_id=str(six_layer_id.session_id),
            channel_type=six_layer_id.channel_type,
            content=content,
            content_type=content_type,
            timestamp=timestamp,
            meta=self._extract_metadata(raw_message),
        )
    
    async def convert_from_bus_message(
        self,
        message: BusMessage,
    ) -> Dict[str, Any]:
        """
        BusMessage v3 → 钉钉消息
        
        Args:
            message: BusMessage v3
        
        Returns:
            钉钉消息格式
        """
        content_type = message.content_type or "text"
        
        if content_type == "text":
            return {
                "msgtype": "text",
                "text": {
                    "content": message.content,
                },
            }
        
        elif content_type == "markdown":
            return {
                "msgtype": "markdown",
                "markdown": {
                    "title": "消息",
                    "text": message.content,
                },
            }
        
        elif content_type == "image":
            # 假设 content 是图片 URL 或 base64
            return {
                "msgtype": "image",
                "image": {
                    "media_id": message.content,
                },
            }
        
        elif content_type == "file":
            return {
                "msgtype": "file",
                "file": {
                    "media_id": message.content,
                },
            }
        
        else:
            # 默认文本
            return {
                "msgtype": "text",
                "text": {
                    "content": message.content,
                },
            }
    
    def _extract_six_layer_id(
        self,
        raw_message: Dict[str, Any],
    ) -> Identifiers:
        """从钉钉消息提取六层标识符"""
        # 钉钉消息结构
        # {
        #     "conversationId": "cid_xxx",
        #     "senderId": "sid_xxx",
        #     "senderNick": "发送者昵称",
        #     "robotCode": "robot_xxx",
        #     "messageId": "msg_xxx",
        #     "createTime": "2026-03-31T10:00:00+08:00",
        #     ...
        # }
        
        conversation_id = raw_message.get("conversationId", "unknown")
        sender_id = raw_message.get("senderId", "unknown")
        robot_code = raw_message.get("robotCode", self.robot_code)
        message_id = raw_message.get("messageId", self._generate_message_id())
        
        # 生成 session_id（从 conversation_id 派生）
        session_id = self._generate_session_id_from_conversation(conversation_id)
        
        return Identifiers(
            channel_id=ChannelId(self.PLATFORM_ID),
            caller_logical_id=CallerLogicalId(
                f"user_{sender_id}",
                caller_type=CallerType.USER,
            ),
            caller_physical_id=CallerPhysicalId(f"user_{sender_id}"),
            called_id=CalledId(robot_code),
            session_id=SessionId(session_id),
            message_id=MessageId(message_id),
            channel_type="private",
        )
    
    def _generate_session_id_from_conversation(
        self,
        conversation_id: str,
    ) -> str:
        """从 conversation_id 生成 session_id"""
        import hashlib
        # 使用 conversation_id 的哈希作为 session_id
        hash_obj = hashlib.md5(conversation_id.encode())
        return f"sess_{hash_obj.hexdigest()[:16]}"
    
    def _extract_content(
        self,
        raw_message: Dict[str, Any],
    ) -> str:
        """提取消息内容"""
        # 文本消息
        if "text" in raw_message:
            return raw_message["text"].get("content", "")
        
        # Markdown 消息
        if "markdown" in raw_message:
            return raw_message["markdown"].get("text", "")
        
        # 图片消息
        if "image" in raw_message:
            return raw_message["image"].get("mediaId", "")
        
        # 文件消息
        if "file" in raw_message:
            return raw_message["file"].get("fileName", "")
        
        # 兼容 ChatbotMessage 对象
        if hasattr(raw_message, "text"):
            return raw_message.text or ""
        
        return ""
    
    def _extract_content_type(
        self,
        raw_message: Dict[str, Any],
    ) -> str:
        """提取内容类型"""
        # 从 msgtype 判断
        msgtype = raw_message.get("msgtype", "text")
        
        if msgtype == "text":
            return "text"
        elif msgtype == "markdown":
            return "markdown"
        elif msgtype == "image":
            return "image"
        elif msgtype == "file":
            return "file"
        elif msgtype == "link":
            return "link"
        else:
            return "text"
    
    def _extract_timestamp(
        self,
        raw_message: Dict[str, Any],
    ) -> datetime:
        """提取时间戳"""
        create_time = raw_message.get("createTime")
        return self._parse_timestamp(create_time)
    
    def _extract_metadata(
        self,
        raw_message: Dict[str, Any],
    ) -> Dict[str, Any]:
        """提取元数据"""
        return {
            "senderNick": raw_message.get("senderNick", ""),
            "senderStaffId": raw_message.get("senderStaffId", ""),
            "conversationTitle": raw_message.get("conversationTitle", ""),
            "chatbotUserId": raw_message.get("chatbotUserId", ""),
            "msgtype": raw_message.get("msgtype", "text"),
        }
    
    def validate_message(
        self,
        raw_message: Dict[str, Any],
    ) -> bool:
        """验证钉钉消息有效性"""
        if not super().validate_message(raw_message):
            return False
        
        # 钉钉消息必须有 conversationId 和 senderId
        if "conversationId" not in raw_message:
            return False
        
        if "senderId" not in raw_message:
            return False
        
        return True
