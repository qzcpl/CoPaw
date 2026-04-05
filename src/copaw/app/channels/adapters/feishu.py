"""
飞书适配器

实现飞书消息与 BusMessage v3 之间的转换
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


class FeishuAdapter(BaseAdapter):
    """
    飞书适配器
    
    支持消息类型：
    - text: 文本消息
    - post: 富文本消息
    - image: 图片消息
    - file: 文件消息
    - share_chat: 分享聊天消息
    
    六层标识符映射：
    - channel_id: "feishu"
    - caller_logical_id: chat_id（群聊/私聊 ID）
    - caller_physical_id: sender_id（发送者 ID）
    - called_id: app_id（应用 ID）
    - session_id: 从 chat_id 生成
    - message_id: message_id（飞书消息 ID）
    """
    
    PLATFORM_ID = "feishu"
    SUPPORTS_MARKDOWN = True
    SUPPORTS_IMAGE = True
    SUPPORTS_FILE = True
    SUPPORTS_VOICE = False
    
    def _init_config(self):
        """初始化配置"""
        self.app_id = self.config.get("app_id", "")
        self.media_dir = self.config.get("media_dir", "")
    
    async def convert_to_bus_message(
        self,
        raw_message: Dict[str, Any],
    ) -> BusMessage:
        """
        飞书消息 → BusMessage v3
        
        Args:
            raw_message: 飞书原始消息
        
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
        BusMessage v3 → 飞书消息
        
        Args:
            message: BusMessage v3
        
        Returns:
            飞书消息格式
        """
        content_type = message.content_type or "text"
        
        if content_type == "text":
            return {
                "msg_type": "text",
                "content": {
                    "text": message.content,
                },
            }
        
        elif content_type == "post":
            return {
                "msg_type": "post",
                "content": {
                    "post": {
                        "zh_cn": {
                            "title": "",
                            "content": [
                                [{"tag": "text", "text": message.content}],
                            ],
                        },
                    },
                },
            }
        
        elif content_type == "image":
            return {
                "msg_type": "image",
                "content": {
                    "image_key": message.content,
                },
            }
        
        elif content_type == "file":
            return {
                "msg_type": "file",
                "content": {
                    "file_key": message.content,
                },
            }
        
        else:
            # 默认文本
            return {
                "msg_type": "text",
                "content": {
                    "text": message.content,
                },
            }
    
    def _extract_six_layer_id(
        self,
        raw_message: Dict[str, Any],
    ) -> Identifiers:
        """从飞书消息提取六层标识符"""
        # 飞书消息结构
        # {
        #     "header": {...},
        #     "event": {
        #         "message": {
        #             "message_id": "msg_xxx",
        #             "chat_id": "chat_xxx",
        #             "sender": {
        #                 "id": "ou_xxx",
        #                 "user_id": "ou_xxx",
        #             },
        #         },
        #     },
        # }
        
        event = raw_message.get("event", {})
        message = event.get("message", {})
        sender = message.get("sender", {})
        
        chat_id = message.get("chat_id", "unknown")
        sender_id = sender.get("user_id", sender.get("id", "unknown"))
        message_id = message.get("message_id", self._generate_message_id())
        
        # 生成 session_id
        session_id = self._generate_session_id_from_chat(chat_id)
        
        return Identifiers(
            channel_id=ChannelId(self.PLATFORM_ID),
            caller_logical_id=CallerLogicalId(
                f"user_{sender_id}",
                caller_type=CallerType.USER,
            ),
            caller_physical_id=CallerPhysicalId(f"user_{sender_id}"),
            called_id=CalledId(self.app_id),
            session_id=SessionId(session_id),
            message_id=MessageId(message_id),
            channel_type="private",
        )
    
    def _generate_session_id_from_chat(
        self,
        chat_id: str,
    ) -> str:
        """从 chat_id 生成 session_id"""
        import hashlib
        hash_obj = hashlib.md5(chat_id.encode())
        return f"sess_{hash_obj.hexdigest()[:16]}"
    
    def _extract_content(
        self,
        raw_message: Dict[str, Any],
    ) -> str:
        """提取消息内容"""
        event = raw_message.get("event", {})
        message = event.get("message", {})
        
        # 文本消息
        if "text" in message:
            return message["text"].get("content", "")
        
        # post 消息（富文本）
        if "content" in message:
            content = message["content"]
            if isinstance(content, str):
                import json
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    return ""
            
            # 提取 post 内容
            post_content = content.get("post", {}).get("zh_cn", {})
            elements = post_content.get("content", [])
            texts = []
            for row in elements:
                for element in row:
                    if element.get("tag") == "text":
                        texts.append(element.get("text", ""))
            return "\n".join(texts)
        
        return ""
    
    def _extract_content_type(
        self,
        raw_message: Dict[str, Any],
    ) -> str:
        """提取内容类型"""
        event = raw_message.get("event", {})
        message = event.get("message", {})
        msg_type = message.get("message_type", "text")
        
        if msg_type == "text":
            return "text"
        elif msg_type == "post":
            return "post"
        elif msg_type == "image":
            return "image"
        elif msg_type == "file":
            return "file"
        elif msg_type == "share_chat":
            return "share_chat"
        else:
            return "text"
    
    def _extract_timestamp(
        self,
        raw_message: Dict[str, Any],
    ) -> datetime:
        """提取时间戳"""
        event = raw_message.get("event", {})
        message = event.get("message", {})
        create_time = message.get("create_time")
        return self._parse_timestamp(create_time)
    
    def _extract_metadata(
        self,
        raw_message: Dict[str, Any],
    ) -> Dict[str, Any]:
        """提取元数据"""
        event = raw_message.get("event", {})
        message = event.get("message", {})
        sender = message.get("sender", {})
        
        return {
            "tenant_key": event.get("tenant_key", ""),
            "message_type": message.get("message_type", ""),
            "root_id": message.get("root_id", ""),
            "parent_id": message.get("parent_id", ""),
            "sender_type": sender.get("sender_type", ""),
            "open_id": sender.get("open_id", ""),
            "union_id": sender.get("union_id", ""),
        }
    
    def validate_message(
        self,
        raw_message: Dict[str, Any],
    ) -> bool:
        """验证飞书消息有效性"""
        if not super().validate_message(raw_message):
            return False
        
        # 飞书消息必须有 event.message
        event = raw_message.get("event", {})
        if not event:
            return False
        
        message = event.get("message", {})
        if not message:
            return False
        
        # 必须有 chat_id 和 sender
        if "chat_id" not in message:
            return False
        
        if "sender" not in message:
            return False
        
        return True
