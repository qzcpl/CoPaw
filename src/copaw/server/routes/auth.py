"""
认证 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime

from ..schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    TokenRefreshRequest,
    TokenRefreshResponse,
    UserInfoResponse,
)
from ..core.security import verify_password, hash_password, create_access_token, decode_access_token
from ..core.exceptions import ApiError, ApiErrorCode
from ..dependencies import get_current_user

router = APIRouter()

# 模拟用户数据库（实际实现应使用数据库）
USERS_DB = {
    "admin": {
        "user_id": "user_admin",
        "username": "admin",
        "password_hash": hash_password("admin123456"),
        "tenant_id": "default",
        "role": "system_admin",
        "created_at": "2026-01-01T00:00:00Z",
        "last_login_at": None,
    }
}


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    用户登录
    
    Args:
        request: 登录请求（用户名、密码、租户 ID）
    
    Returns:
        登录响应（Token、用户信息）
    """
    # 查询用户
    user = USERS_DB.get(request.username)
    
    if not user:
        raise ApiError(
            code=ApiErrorCode.AUTH_FAILED,
            message="Invalid username or password",
            status_code=401,
        )
    
    # 验证密码
    if not verify_password(request.password, user["password_hash"]):
        raise ApiError(
            code=ApiErrorCode.AUTH_FAILED,
            message="Invalid username or password",
            status_code=401,
        )
    
    # 验证租户
    if user["tenant_id"] != request.tenant_id:
        raise ApiError(
            code=ApiErrorCode.TENANT_ACCESS_DENIED,
            message=f"User not found in tenant: {request.tenant_id}",
            status_code=403,
        )
    
    # 生成 JWT Token
    token = create_access_token(
        user_id=user["user_id"],
        tenant_id=user["tenant_id"],
        role=user["role"],
    )
    
    # 更新最后登录时间
    user["last_login_at"] = datetime.utcnow().isoformat() + "Z"
    
    return LoginResponse(
        token=token,
        token_type="bearer",
        user_id=user["user_id"],
        tenant_id=user["tenant_id"],
        role=user["role"],
    )


@router.post("/register", response_model=LoginResponse)
async def register(request: RegisterRequest):
    """
    用户注册
    
    Args:
        request: 注册请求（用户名、密码、租户 ID）
    
    Returns:
        登录响应（Token、用户信息）
    """
    # 检查用户名是否已存在
    if request.username in USERS_DB:
        raise ApiError(
            code=ApiErrorCode.AUTH_FAILED,
            message="Username already exists",
            status_code=400,
        )
    
    # 创建用户
    user_id = f"user_{request.username}_{int(datetime.utcnow().timestamp())}"
    user = {
        "user_id": user_id,
        "username": request.username,
        "password_hash": hash_password(request.password),
        "tenant_id": request.tenant_id,
        "role": "user",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "last_login_at": None,
    }
    
    USERS_DB[request.username] = user
    
    # 生成 JWT Token
    token = create_access_token(
        user_id=user_id,
        tenant_id=request.tenant_id,
        role="user",
    )
    
    return LoginResponse(
        token=token,
        token_type="bearer",
        user_id=user_id,
        tenant_id=request.tenant_id,
        role="user",
    )


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(request: TokenRefreshRequest):
    """
    刷新 Token
    
    Args:
        request: 刷新请求（旧 Token）
    
    Returns:
        新 Token
    """
    # 验证旧 Token
    payload = decode_access_token(request.token)
    
    if not payload:
        raise ApiError(
            code=ApiErrorCode.TOKEN_INVALID,
            message="Invalid token",
            status_code=401,
        )
    
    # 生成新 Token
    new_token = create_access_token(
        user_id=payload["sub"],
        tenant_id=payload["tenant_id"],
        role=payload["role"],
    )
    
    return TokenRefreshResponse(
        token=new_token,
        token_type="bearer",
    )


@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    获取当前用户信息
    
    Args:
        current_user: 当前用户（从 JWT 解析）
    
    Returns:
        用户信息
    """
    # 查询用户详情
    user = None
    for u in USERS_DB.values():
        if u["user_id"] == current_user["user_id"]:
            user = u
            break
    
    if not user:
        raise ApiError(
            code=ApiErrorCode.NOT_FOUND,
            message="User not found",
            status_code=404,
        )
    
    return UserInfoResponse(
        user_id=user["user_id"],
        tenant_id=user["tenant_id"],
        role=user["role"],
        username=user["username"],
        created_at=user["created_at"],
        last_login_at=user["last_login_at"] or "",
    )
