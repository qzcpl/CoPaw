"""
租户隔离中间件
"""
from fastapi import Request
import logging

logger = logging.getLogger(__name__)


# 跳过租户检查的路径
SKIP_TENANT_PATHS = [
    "/auth/login",
    "/auth/register",
    "/health",
    "/docs",
    "/redoc",
    "/",
]


async def tenant_middleware(request: Request, call_next):
    """
    租户隔离中间件
    
    从 Header 或 Token 中获取租户 ID，设置到 request.state
    后续数据库查询自动添加 tenant_id 过滤
    """
    # 检查是否需要跳过
    if any(request.url.path.startswith(path) for path in SKIP_TENANT_PATHS):
        return await call_next(request)
    
    # 优先从 Header 获取租户 ID（前端传递）
    tenant_id = request.headers.get("X-Tenant-ID")
    
    # 如果 Header 没有，从 Token 中获取
    if not tenant_id and hasattr(request.state, "tenant_id"):
        tenant_id = request.state.tenant_id
    
    # 如果还是没有，使用默认租户
    if not tenant_id:
        tenant_id = "default"
        logger.debug(f"No tenant_id provided, using default for path: {request.url.path}")
    
    # 设置到 request.state
    request.state.tenant_id = tenant_id
    
    return await call_next(request)


def get_tenant_id(request: Request) -> str:
    """
    获取当前请求的租户 ID
    
    Args:
        request: FastAPI Request 对象
    
    Returns:
        租户 ID
    """
    return getattr(request.state, "tenant_id", "default")
