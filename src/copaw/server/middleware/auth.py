"""
JWT 认证中间件
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from datetime import datetime
import logging

from ..config import settings

logger = logging.getLogger(__name__)


# 跳过认证的路径
SKIP_AUTH_PATHS = [
    "/auth/login",
    "/auth/register",
    "/auth/refresh",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/",
]


async def auth_middleware(request: Request, call_next):
    """
    JWT 认证中间件
    
    从 Authorization Header 中提取 JWT Token，验证后设置用户信息到 request.state
    """
    # 检查是否需要跳过认证
    if any(request.url.path.startswith(path) for path in SKIP_AUTH_PATHS):
        return await call_next(request)
    
    # 提取 Authorization Header
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return JSONResponse(
            status_code=401,
            content={
                "code": "AUTH_FAILED",
                "message": "Authorization header required",
            },
        )
    
    # 验证 Bearer 格式
    if not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={
                "code": "AUTH_FAILED",
                "message": "Invalid authorization format. Use: Bearer <token>",
            },
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        # 解码 JWT Token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        
        # 提取用户信息
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id")
        role = payload.get("role", "user")
        
        if not user_id or not tenant_id:
            from ..core.exceptions import ApiError, ApiErrorCode
            raise ApiError(
                code=ApiErrorCode.TOKEN_INVALID,
                message="Invalid token payload",
                status_code=401,
            )
        
        # 设置到 request.state，供后续使用
        request.state.user_id = user_id
        request.state.tenant_id = tenant_id
        request.state.role = role
        request.state.token_payload = payload
        
    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        return JSONResponse(
            status_code=401,
            content={
                "code": "TOKEN_EXPIRED",
                "message": "Token expired or invalid",
            },
        )
    except Exception as e:
        logger.exception(f"Auth middleware error: {e}")
        return JSONResponse(
            status_code=401,
            content={
                "code": "AUTH_FAILED",
                "message": str(e),
            },
        )
    
    return await call_next(request)
