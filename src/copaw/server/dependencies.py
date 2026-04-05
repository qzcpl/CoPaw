"""
FastAPI 依赖注入
"""
from fastapi import Depends, Request, HTTPException
from typing import Optional


async def get_current_user(request: Request) -> dict:
    """
    获取当前用户（从 request.state）
    
    由 auth_middleware 设置
    """
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "user_id": user_id,
        "tenant_id": getattr(request.state, "tenant_id", "default"),
        "role": getattr(request.state, "role", "user"),
    }


async def require_permission(required_role: str):
    """
    权限检查依赖
    
    Args:
        required_role: 所需角色（tenant_admin/system_admin）
    """
    def dependency(current_user: dict = Depends(get_current_user)):
        role_hierarchy = {
            "guest": 0,
            "user": 1,
            "tenant_admin": 2,
            "system_admin": 3,
        }
        
        user_level = role_hierarchy.get(current_user["role"], 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: {required_role} required",
            )
        
        return current_user
    
    return dependency


# 快捷依赖
require_tenant_admin = Depends(require_permission("tenant_admin"))
require_system_admin = Depends(require_permission("system_admin"))
