"""
安全模块：JWT 和密码处理
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext

from .config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
    
    Returns:
        是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """
    哈希密码
    
    Args:
        password: 明文密码
    
    Returns:
        哈希密码
    """
    return pwd_context.hash(password)


def create_access_token(
    user_id: str,
    tenant_id: str,
    role: str = "user",
    expires_delta: Optional[int] = None,
) -> str:
    """
    创建 JWT Access Token
    
    Args:
        user_id: 用户 ID
        tenant_id: 租户 ID
        role: 用户角色（user/tenant_admin/system_admin）
        expires_delta: 过期时间（秒），默认使用配置值
    
    Returns:
        JWT Token 字符串
    """
    if expires_delta is None:
        expires_delta = settings.JWT_EXPIRATION_MINUTES * 60
    
    expire = datetime.utcnow() + timedelta(seconds=expires_delta)
    
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "role": role,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    
    return token


def decode_access_token(token: str) -> Optional[dict]:
    """
    解码 JWT Access Token
    
    Args:
        token: JWT Token
    
    Returns:
        Token Payload，如果无效则返回 None
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except Exception:
        return None
