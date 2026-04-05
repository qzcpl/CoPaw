"""
数据库连接管理

提供数据库连接、会话管理和表创建
"""

from typing import Optional
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# 全局变量
_engine = None
_SessionLocal = None
Base = declarative_base()


def init_database(database_url: str, echo: bool = False):
    """
    初始化数据库连接
    
    Args:
        database_url: 数据库 URL（如 sqlite:///copaw.db）
        echo: 是否打印 SQL 日志
    """
    global _engine, _SessionLocal
    
    _engine = create_engine(
        database_url,
        echo=echo,
        pool_pre_ping=True,  # 连接前 ping 测试
        pool_recycle=3600,   # 1 小时后回收连接
    )
    
    _SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=_engine,
    )
    
    # 创建所有表
    Base.metadata.create_all(bind=_engine)


def get_engine():
    """获取数据库引擎"""
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _engine


def get_session() -> Session:
    """获取数据库会话"""
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return _SessionLocal()


@contextmanager
def session_scope():
    """
    会话上下文管理器
    
    自动处理提交、回滚和关闭
    
    Usage:
        with session_scope() as session:
            session.add(obj)
    """
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_tables():
    """创建所有数据库表"""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """删除所有数据库表（危险操作！）"""
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
