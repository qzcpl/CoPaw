"""
CoPaw 标识符模块

提供六层标识体系的数据结构、生成器和验证器
"""

from .schemas import (
    ChannelId,
    CallerLogicalId,
    CallerPhysicalId,
    CalledId,
    SessionId,
    MessageId,
    Identifiers,
)
from .generator import IdentifierGenerator
from .validator import IdentifierValidator

__all__ = [
    "ChannelId",
    "CallerLogicalId",
    "CallerPhysicalId",
    "CalledId",
    "SessionId",
    "MessageId",
    "Identifiers",
    "IdentifierGenerator",
    "IdentifierValidator",
]
