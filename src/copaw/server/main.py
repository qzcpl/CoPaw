"""
CoPaw HTTP API Server
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from .middleware.auth import auth_middleware
from .middleware.tenant import tenant_middleware
from .middleware.logging import logging_middleware
from .core.exceptions import ApiError, ApiErrorCode
from .routes import (
    auth, callid, bot, tenant, queue, 
    monitor, routing, gray_release, chat
)
from .config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("CoPaw API Server starting...")
    
    # 初始化数据库连接
    # 初始化 Redis 连接
    # 初始化 ChannelManager
    
    yield
    
    # 关闭时清理
    logger.info("CoPaw API Server shutting down...")
    # 关闭数据库连接
    # 关闭 Redis 连接


# 创建 FastAPI 应用
app = FastAPI(
    title="CoPaw API",
    description="CoPaw Channel Architecture REST API",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS 配置（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Tenant-ID", "X-Agent-Id"],
)

# 注册中间件
app.middleware("http")(logging_middleware)
app.middleware("http")(auth_middleware)
app.middleware("http")(tenant_middleware)

# 注册路由
app.include_router(auth.router, prefix="/auth", tags=["认证"])
app.include_router(callid.router, prefix="/callid", tags=["callId 管理"])
app.include_router(bot.router, prefix="/bots", tags=["Bot 管理"])
app.include_router(tenant.router, prefix="/tenants", tags=["租户管理"])
app.include_router(queue.router, prefix="/queues", tags=["队列管理"])
app.include_router(monitor.router, prefix="/monitor", tags=["监控"])
app.include_router(routing.router, prefix="/routing", tags=["路由配置"])
app.include_router(gray_release.router, prefix="/gray_release", tags=["灰度发布"])
app.include_router(chat.router, prefix="/chat", tags=["聊天"])


# 全局异常处理
@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    """统一处理 API 错误"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code.value,
            "message": exc.message,
            "details": exc.details,
            "path": request.url.path,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理未预期的异常"""
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_ERROR",
            "message": "Internal server error",
            "path": request.url.path,
        },
    )


# 健康检查
@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "version": "2.0.0",
    }


# 根路径
@app.get("/", tags=["根路径"])
async def root():
    """API 根路径"""
    return {
        "name": "CoPaw API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# 启动命令
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "copaw.server.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
