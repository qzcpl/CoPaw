"""
请求日志中间件
"""
from fastapi import Request
import logging
import time
import json

logger = logging.getLogger(__name__)


async def logging_middleware(request: Request, call_next):
    """
    请求日志中间件
    
    记录每个请求的详细信息，用于审计和调试
    """
    # 记录请求开始时间
    start_time = time.time()
    
    # 提取请求信息
    method = request.method
    path = request.url.path
    query = str(request.url.query) if request.url.query else ""
    client_host = request.client.host if request.client else "unknown"
    
    # 记录请求
    logger.info(
        f"REQUEST: {method} {path}"
        f"{f'?{query}' if query else ''}"
        f" from {client_host}"
    )
    
    # 处理请求
    try:
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录响应
        logger.info(
            f"RESPONSE: {method} {path} "
            f"status={response.status_code} "
            f"time={process_time:.3f}s"
        )
        
        # 添加处理时间到响应头
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.exception(
            f"ERROR: {method} {path} "
            f"time={process_time:.3f}s "
            f"error={str(e)}"
        )
        raise
