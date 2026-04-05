"""
自定义异常
"""
from enum import Enum
from typing import Optional, Dict, Any


class ApiErrorCode(str, Enum):
    """API 错误码"""
    
    # 认证相关
    AUTH_FAILED = "AUTH_FAILED"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    
    # callId 相关
    CALLID_ALREADY_BOUND = "CALLID_ALREADY_BOUND"
    CALLID_NOT_FOUND = "CALLID_NOT_FOUND"
    CALLID_SWITCH_FAILED = "CALLID_SWITCH_FAILED"
    CALLID_SUSPEND_FAILED = "CALLID_SUSPEND_FAILED"
    CALLID_RESUME_FAILED = "CALLID_RESUME_FAILED"
    
    # Bot 相关
    BOT_NOT_FOUND = "BOT_NOT_FOUND"
    BOT_ALREADY_EXISTS = "BOT_ALREADY_EXISTS"
    BOT_CONNECT_FAILED = "BOT_CONNECT_FAILED"
    
    # 租户相关
    TENANT_NOT_FOUND = "TENANT_NOT_FOUND"
    TENANT_ACCESS_DENIED = "TENANT_ACCESS_DENIED"
    TENANT_ALREADY_EXISTS = "TENANT_ALREADY_EXISTS"
    
    # 队列相关
    QUEUE_FULL = "QUEUE_FULL"
    QUEUE_NOT_FOUND = "QUEUE_NOT_FOUND"
    QUEUE_CONFIG_INVALID = "QUEUE_CONFIG_INVALID"
    
    # 监控相关
    METRIC_NOT_FOUND = "METRIC_NOT_FOUND"
    ALERT_NOT_FOUND = "ALERT_NOT_FOUND"
    
    # 路由相关
    ROUTING_STRATEGY_NOT_FOUND = "ROUTING_STRATEGY_NOT_FOUND"
    ROUTING_CONFIG_INVALID = "ROUTING_CONFIG_INVALID"
    
    # 通用
    INTERNAL_ERROR = "INTERNAL_ERROR"
    INVALID_PARAMS = "INVALID_PARAMS"
    NOT_FOUND = "NOT_FOUND"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"


class ApiError(Exception):
    """API 错误基类"""
    
    def __init__(
        self,
        code: ApiErrorCode,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# 快捷错误类
class NotFoundError(ApiError):
    def __init__(self, resource: str, id: str):
        super().__init__(
            code=ApiErrorCode.NOT_FOUND,
            message=f"{resource} not found: {id}",
            status_code=404,
            details={"resource": resource, "id": id},
        )


class PermissionDeniedError(ApiError):
    def __init__(self, required_permission: str):
        super().__init__(
            code=ApiErrorCode.PERMISSION_DENIED,
            message=f"Permission denied: {required_permission} required",
            status_code=403,
            details={"required_permission": required_permission},
        )
