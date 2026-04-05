"""
认证相关 Schema
"""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求"""
    
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    tenant_id: str = Field(default="default")


class LoginResponse(BaseModel):
    """登录响应"""
    
    token: str
    token_type: str = "bearer"
    user_id: str
    tenant_id: str
    role: str


class RegisterRequest(BaseModel):
    """注册请求"""
    
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    tenant_id: str = Field(default="default")


class TokenRefreshRequest(BaseModel):
    """Token 刷新请求"""
    
    token: str


class TokenRefreshResponse(BaseModel):
    """Token 刷新响应"""
    
    token: str
    token_type: str = "bearer"


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    
    user_id: str
    tenant_id: str
    role: str
    username: str
    created_at: str
    last_login_at: str
