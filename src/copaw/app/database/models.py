"""
数据库模型定义

定义 5 张核心表：
1. identifier_registry - 标识符注册表（called_id 路由）
2. session_records - 会话记录表
3. message_logs - 消息日志表
4. channel_configs - 频道配置表
5. agent_bindings - Agent 绑定表
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Boolean,
    Text,
    JSON,
    Index,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from .connection import Base


class IdentifierRegistry(Base):
    """
    标识符注册表（CalledId 路由表）
    
    实现"携号转网"机制：called_id 不变，背后 Agent 可动态切换
    
    字段：
        id: 主键
        called_id: 被叫 ID（400-001 等），唯一
        agent_id: 绑定的 Agent ID
        priority: 优先级（负载均衡）
        weight: 权重（0-100）
        is_active: 是否激活
        metadata: 扩展元数据
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "identifier_registry"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    called_id = Column(String(64), unique=True, nullable=False, index=True)
    agent_id = Column(String(64), nullable=False)
    priority = Column(Integer, default=0)
    weight = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index("idx_called_id_active", "called_id", "is_active"),
    )
    
    def __repr__(self):
        return f"<IdentifierRegistry(called_id={self.called_id}, agent_id={self.agent_id})>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "called_id": self.called_id,
            "agent_id": self.agent_id,
            "priority": self.priority,
            "weight": self.weight,
            "is_active": self.is_active,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class SessionRecord(Base):
    """
    会话记录表
    
    记录会话的完整信息，支持会话穿透
    
    字段：
        id: 主键
        session_id: 会话 ID，唯一
        channel_id: 频道 ID
        caller_logical_id: 逻辑主叫 ID
        caller_physical_id: 物理主叫 ID
        called_id: 被叫 ID
        channel_type: 会话类型（private/group）
        group_id: 群 ID（群聊场景）
        status: 会话状态（active/closed/timeout）
        message_count: 消息数量
        metadata: 扩展元数据
        started_at: 开始时间
        last_active_at: 最后活跃时间
        closed_at: 结束时间
    """
    __tablename__ = "session_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(128), unique=True, nullable=False, index=True)
    channel_id = Column(String(64), nullable=False)
    caller_logical_id = Column(String(128), nullable=False)
    caller_physical_id = Column(String(128), nullable=False)
    called_id = Column(String(64), nullable=False)
    channel_type = Column(String(16), default="private")
    group_id = Column(String(128), nullable=True)
    status = Column(String(16), default="active")
    message_count = Column(Integer, default=0)
    metadata = Column(JSON, default=dict)
    started_at = Column(DateTime, server_default=func.now())
    last_active_at = Column(DateTime, server_default=func.now())
    closed_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index("idx_session_caller", "caller_logical_id", "started_at"),
        Index("idx_session_called", "called_id", "started_at"),
        Index("idx_session_status", "status", "last_active_at"),
    )
    
    def __repr__(self):
        return f"<SessionRecord(session_id={self.session_id}, status={self.status})>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "channel_id": self.channel_id,
            "caller_logical_id": self.caller_logical_id,
            "caller_physical_id": self.caller_physical_id,
            "called_id": self.called_id,
            "channel_type": self.channel_type,
            "group_id": self.group_id,
            "status": self.status,
            "message_count": self.message_count,
            "metadata": self.metadata,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_active_at": self.last_active_at.isoformat() if self.last_active_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
        }


class MessageLog(Base):
    """
    消息日志表
    
    记录所有消息的完整信息，支持消息追踪和审计
    
    字段：
        id: 主键
        message_id: 消息 ID，唯一
        session_id: 会话 ID
        channel_id: 频道 ID
        caller_logical_id: 逻辑主叫 ID
        caller_physical_id: 物理主叫 ID
        called_id: 被叫 ID
        content: 消息内容
        content_type: 内容类型（text/image/file 等）
        direction: 消息方向（inbound/outbound）
        status: 消息状态（sent/delivered/failed）
        metadata: 扩展元数据
        created_at: 创建时间
    """
    __tablename__ = "message_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(String(128), unique=True, nullable=False, index=True)
    session_id = Column(String(128), nullable=False, index=True)
    channel_id = Column(String(64), nullable=False)
    caller_logical_id = Column(String(128), nullable=False)
    caller_physical_id = Column(String(128), nullable=False)
    called_id = Column(String(64), nullable=False)
    content = Column(Text, nullable=True)
    content_type = Column(String(32), default="text")
    direction = Column(String(16), default="inbound")
    status = Column(String(16), default="sent")
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    __table_args__ = (
        Index("idx_message_session", "session_id", "created_at"),
        Index("idx_message_caller", "caller_physical_id", "created_at"),
        Index("idx_message_status", "status", "created_at"),
    )
    
    def __repr__(self):
        return f"<MessageLog(message_id={self.message_id}, status={self.status})>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "message_id": self.message_id,
            "session_id": self.session_id,
            "channel_id": self.channel_id,
            "caller_logical_id": self.caller_logical_id,
            "caller_physical_id": self.caller_physical_id,
            "called_id": self.called_id,
            "content": self.content,
            "content_type": self.content_type,
            "direction": self.direction,
            "status": self.status,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ChannelConfig(Base):
    """
    频道配置表
    
    动态管理频道配置，支持热更新
    
    字段：
        id: 主键
        channel_id: 频道 ID，唯一
        channel_type: 频道类型
        config: 配置内容（JSON）
        is_enabled: 是否启用
        metadata: 扩展元数据
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "channel_configs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(String(64), unique=True, nullable=False, index=True)
    channel_type = Column(String(32), nullable=False)
    config = Column(JSON, default=dict)
    is_enabled = Column(Boolean, default=True)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index("idx_channel_type", "channel_type", "is_enabled"),
    )
    
    def __repr__(self):
        return f"<ChannelConfig(channel_id={self.channel_id}, type={self.channel_type})>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "channel_id": self.channel_id,
            "channel_type": self.channel_type,
            "config": self.config,
            "is_enabled": self.is_enabled,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class AgentBinding(Base):
    """
    Agent 绑定表
    
    管理 Agent 与频道的绑定关系，支持多租户
    
    字段：
        id: 主键
        agent_id: Agent ID
        channel_id: 频道 ID
        called_id: 被叫 ID（可选）
        tenant_id: 租户 ID（多租户支持）
        priority: 优先级
        is_active: 是否激活
        metadata: 扩展元数据
        created_at: 创建时间
        updated_at: 更新时间
    """
    __tablename__ = "agent_bindings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(64), nullable=False)
    channel_id = Column(String(64), nullable=False)
    called_id = Column(String(64), nullable=True)
    tenant_id = Column(String(64), nullable=True)
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint("agent_id", "channel_id", "called_id", name="uq_agent_channel_called"),
        Index("idx_agent_active", "agent_id", "is_active"),
        Index("idx_channel_active", "channel_id", "is_active"),
        Index("idx_tenant_active", "tenant_id", "is_active"),
    )
    
    def __repr__(self):
        return f"<AgentBinding(agent_id={self.agent_id}, channel_id={self.channel_id})>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "channel_id": self.channel_id,
            "called_id": self.called_id,
            "tenant_id": self.tenant_id,
            "priority": self.priority,
            "is_active": self.is_active,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
