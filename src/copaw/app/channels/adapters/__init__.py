"""
频道适配器模块

提供各平台消息格式与 BusMessage v3 之间的转换
"""

from .base import BaseAdapter
from .console import ConsoleAdapter
from .dingtalk import DingTalkAdapter
from .feishu import FeishuAdapter

__all__ = [
    "BaseAdapter",
    "ConsoleAdapter",
    "DingTalkAdapter",
    "FeishuAdapter",
]
